<!--
Sync Impact Report
Version change: 1.2.0 → 1.3.0
Modified principles:
   - VII. Identity & Access Control → expanded with role taxonomy (dev, admin, user, readonly),
     always-available accounts (one dev, one admin), and break-glass emergency accounts (one dev, one admin)
     to prevent operator lockout scenarios.
Added sections:
   - Role-Based Access Matrix subsection under Principle VII
   - Always-Available Accounts subsection under Principle VII
   - Break-Glass Emergency Access subsection under Principle VII
   - Lockout Prevention constraints in Additional Technical & Quality Constraints (items 17-19)
Removed sections: None
Templates requiring updates:
   - .specify/templates/plan-template.md ✅ (already has identity compliance prompts)
   - .specify/templates/spec-template.md ✅ (already documents auth requirements + security section)
   - .specify/templates/tasks-template.md ✅ (already has identity task rules and validation)
Follow-up TODOs:
   1. TODO(AUTH_DOCS): Publish operator guide for account provisioning/reset (docs/authentication.md) once CLI tooling is finalized.
   2. TODO(BREAK_GLASS_PROCEDURE): Document sealed-envelope storage and rotation procedure for break-glass credentials.
   3. TODO(ROLE_MIGRATION): Add migration scripts to provision always-available and break-glass accounts in existing databases.
-->

# RFU (Richard's File Utilities) Constitution

## Core Principles

### I. Cross-Platform Consistency

All supported operating systems (Windows, macOS, Linux) MUST deliver identical
functional capabilities (feature flags may only disable OS-infeasible actions).
UI labels, shortcuts (where feasible), and behaviors MUST remain consistent.
Platform-specific code MUST be isolated behind clearly named adapter modules.
Rationale: Predictable behavior across environments reduces user friction and
lowers maintenance cost by preventing divergent code paths.

### II. Safety & Data Integrity (NON‑NEGOTIABLE)

Destructive operations (delete, secure wipe, overwrite) MUST be opt-in and
require explicit user confirmation (or a signed CLI flag in headless mode).
Default behavior for move/copy/sync MUST preserve source data unless user
chooses otherwise. Secure deletion MUST use verified overwrite patterns.
All operations MUST support dry‑run simulation. Metadata manipulations MUST
validate schema before commit. Rationale: File utilities operate on critical
user assets; irreversible loss must be virtually eliminated.

### III. Test-Driven Quality & Observability

All new functionality MUST begin with failing automated tests (unit and where
relevant integration). Minimum global line coverage MUST remain ≥ 85% and MUST
not decrease in a PR. Critical engines (duplicate detection, secure delete,
batch processors) MUST have property-based or scenario edge tests. Structured
logging (levelled, machine-parsable) and error classification MUST accompany
features. Rationale: Fast feedback and rich telemetry enable safe evolution.

### IV. Performance & Scalability of Batch Operations

Core batch operations (search, duplicate scan, metadata extraction, copying)
MUST stream and avoid loading entire directory trees or large files wholly in
memory. Operations on N files MUST scale approximately O(N) with clear
progress reporting. UI interactions MUST stay responsive (no blocking main GUI
thread > 100ms; use worker threads/process pools). Rationale: User trust and
enterprise viability depend on predictable performance under large workloads.

### V. Simplicity & Extensible Modularity

Features MUST be implemented as modular, discoverable tool components with
clear single responsibility. Public interfaces (CLI / scripted APIs) MUST be
stable; changes require deprecation cycle (see Governance). Avoid premature
generalization: implement minimum set that satisfies explicit requirements.
Extension points (tool discovery, engines, PyQt5 GUI registration) MUST
document contracts and failure modes with automated validation before launch.
Rationale: Lean, modular design reduces coupling and accelerates safe
innovation. For PyQt5-based tools: use `{ToolName}GUI` naming convention,
auto-discovery via metadata patterns, and graceful import fallbacks.

### VI. User Preference Management & Personalization

User personalization is a first-class capability backed by a robust, modular
preference framework:

- Canonical store: Preferences MUST persist in a database table
  (`user_preferences`) with strong namespacing: `user_id`,
  `preference_category`, `preference_key` → `preference_value` + `value_type`.
  Implement triggers to maintain timestamps and use indexes for category/user
  queries. If the database is unavailable, a JSON file fallback MAY be used
  transparently without loss of correctness.
- Extensibility: Modules MUST define preferences under their own category
  namespace (e.g., `theming`, `favorites`, `directories`,
  `module_settings/<module>`). Categories and keys MUST be discoverable via a
  registry API with validation (type, allowed range, default, description).
- Universal theming: A single theme system MUST provide shared tokens (colors,
  typography, spacing) consumed by all modules. Theme storage uses preferences
  under the `theming` category with profile support (named presets) and WCAG AA
  contrast compliance.
- Favorites & directories: Users MUST be able to mark favorites (tools,
  paths, actions) and persist directory preferences (e.g., last opened,
  default start locations, visibility of hidden files) across modules.
- Security & privacy: Sensitive preferences (e.g., encryption settings, saved
  keys paths) MUST be storable as encrypted values with envelope encryption and
  redactable logs. No secrets in plain text; credential material (passwords,
  tokens, recovery phrases) MUST live in the Identity & Access Control layer and
  may only reference preference data through opaque identifiers.
- Migration & compatibility: Preference schemas MUST be versioned. Additive
  changes are MINOR; breaking changes require a migration with fallback
  defaults. Module independence MUST be preserved—each module may evolve its
  preferences without impacting others.

Rationale: A consistent, typed, and discoverable preference layer enables rich
customization while preserving safety, performance, and maintainability across
independent modules.

### VII. Identity & Access Control

Authentication and authorization guard every executable surface and obey the
following non-negotiable rules:

#### Role-Based Access Matrix

The system enforces **four account roles** with distinct privilege levels:

| Role       | Description                                                            | Key Capabilities                                                                     |
| ---------- | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `dev`      | Developer access with full debugging/diagnostic capabilities           | All user + admin capabilities, plus debug logging, diagnostics, and internal tooling |
| `admin`    | Administrator access with user management and configuration privileges | User management, account approval/reset/unblock, configuration changes, audit review |
| `user`     | Standard user access for regular application functionality             | Normal file operations, preference management, tool usage                            |
| `readonly` | Read-only access with no write/modification capabilities               | View-only access to files and reports; no destructive operations                     |

Role assignment MUST be explicit; default new accounts MUST start in a pending
state until approved by an admin. Role escalation (e.g., user → admin) MUST
require admin approval and emit an audit entry.

#### Always-Available Accounts

To prevent operator lockout, **two accounts MUST always be available** and
active at system initialization:

| Account Type | Purpose                                                              |
| ------------ | -------------------------------------------------------------------- |
| **dev**      | Guaranteed developer access for debugging and development operations |
| **admin**    | Guaranteed administrator access for user management and recovery     |

These accounts:

- MUST be provisioned automatically during database initialization or migration.
- MUST NOT be deletable or deactivatable through normal UI/CLI flows.
- MUST have their passwords set via secure operator procedures (not hard-coded).
- MUST emit audit entries for every login and action.
- MAY be renamed but MUST retain their protected status via internal flags.

#### Break-Glass Emergency Access

**Two break-glass accounts** provide emergency recovery when primary accounts
are compromised or locked:

| Account Type | Purpose                                                            |
| ------------ | ------------------------------------------------------------------ |
| **dev**      | Emergency developer access when primary dev account is unavailable |
| **admin**    | Emergency admin access when primary admin account is unavailable   |

Break-glass accounts:

- MUST have credentials stored offline in a sealed envelope or secure vault
  (not in version control, not in config files, not in the database itself).
- MUST be disabled by default and require explicit enablement (CLI flag or
  environment variable) before authentication succeeds.
- MUST trigger an audit alert upon successful login, notifying all active
  admins.
- MUST require immediate password rotation after use; the system SHOULD prompt
  or enforce rotation before allowing continued operation.
- MUST be tested annually to verify credentials remain valid and recovery
  procedures are documented.

#### Credential Storage

- User passwords MUST be hashed with a memory-hard
  algorithm (Argon2id or bcrypt, cost parameters documented per release). No
  plaintext or reversible formats allowed. Password updates MUST rotate salts.

#### Lockout & Monitoring

- After 5 consecutive failed logins the account MUST be
  blocked until an administrator (or automated unlock workflow) resets the
  counter. Each attempt (success or failure) MUST be logged with timestamp and
  origin metadata.
- Always-available and break-glass accounts are subject to the same lockout
  rules but MUST be recoverable via the alternate emergency account (e.g., if
  the always-available admin is locked, the break-glass admin can unblock it).

#### Admin Resets & Unblock

- Administrative resets MUST generate a temporary
  password (or secure reset token) without exposing password hashes. Unblocks
  MUST reset counters, emit audit entries, and confirm actor identity.

#### Preference Linkage

- Each account MUST reference a dedicated preference
  namespace identifier so that personalization never leaks between users. Tying
  a session to preferences MUST happen immediately after authentication.

#### Session Controls

- Long-running sessions MUST support manual logout and idle
  timeout (≤ 30 min default). Tokens or session secrets MUST be stored in
  memory only and cleared on logout or crash recovery.

Rationale: Centralized, auditable identity enforcement prevents privilege
escalation, enforces regulatory requirements, and protects the high-risk file
operations delivered by RFU. The always-available and break-glass accounts
guarantee that operators are never permanently locked out, while maintaining
full audit trails for accountability.

## Additional Technical & Quality Constraints

1. Language & Framework: Python ≥ 3.8, Qt5 GUI. Migration past EOL versions
   MUST be planned before upstream EOL minus 90 days.
2. Code Style: PEP 8 enforced; mypy type checking with no new errors allowed.
3. Security: All external inputs (paths, metadata) MUST be validated; no
   shell command execution without explicit sanitization. Secure delete MUST
   document overwrite algorithm. Sensitive logs MUST be redactable.
4. Logging & Errors: No silent failures; user-facing errors MUST provide
   actionable remediation guidance. Internal stack traces logged at DEBUG+.
5. Coverage & Gates: PRs MUST pass: lint, type check, unit + integration tests,
   coverage ≥ threshold, GUI smoke test (launch + tool open), and tool
   validation (import success + instantiation check). Failing gate → reject.
6. Performance Baselines: Duplicate scanning: ≥ 10k files/min on reference
   dataset (documented). UI main thread blocked < 100ms segments. Long-running
   tasks MUST expose cancellable progress.
7. Accessibility: Key actions reachable via keyboard; color selections MUST
   maintain WCAG AA contrast for text.
8. Documentation: New tools MUST include: purpose, usage examples, expected
   performance characteristics, error codes, and test strategy summary.
9. Dependency Management: New runtime dependency MUST justify: necessity,
   security posture, maintenance health. Vendoring considered for small libs.
10. Backward Compatibility: Public CLI flags and scripting APIs require a
    deprecation period ≥ 1 MINOR release unless security issue mandates fast
    removal.

11. Preference Schema & API:

    - Typed values: `value_type` MUST be enforced (`string`, `int`, `float`,
      `bool`, `json`). Invalid values MUST be rejected at write-time.
    - Namespacing: Categories MUST be kebab-case or snake_case; module-owned
      categories MUST be prefixed with module scope (e.g., `module_settings/af`).
    - Auditability: Preference writes SHOULD emit structured audit events.
    - Caching: Read-through caching MAY be used but MUST invalidate on write.
    - Fallback: When DB is unavailable, JSON fallback MUST mirror API semantics
      and migrate to DB when restored.

12. Data Migration:

    - Schema updates MUST be idempotent and forward-only with version gating.
    - Migrations MUST be tested (up/down where applicable) and time-bounded.
    - On failure, system MUST roll back to a safe checkpoint and surface user
      guidance.

13. Separation of Concerns:

    - Core functionality MUST not embed user-specific defaults; read them via
      the preference API.
    - Modules MUST function with defaults if preferences are absent.

14. Authentication Data Handling:

    - `user_accounts` data MUST reside in the canonical database, keyed by
      username with Argon2id hashes, per-user preference namespace, role, and
      lockout status.
    - Credential APIs MUST never expose password hashes. Administrative tools
      MAY return generated temporary passwords once (on creation/reset) and MUST
      log the actor + delivery channel.
    - Login attempts MUST update `login_attempts`, `last_failed_login`, and
      `is_blocked` atomically. Successful logins reset counters and stamp
      `last_login`.

15. Credential Reset & Account Lifecycle:

    - Password policies: minimum 12 characters, at least 3 character classes,
      reject breached passwords via denylist when network connectivity allows.
    - Reset flow MUST be auditable and require either admin identity proof or a
      signed challenge token.
    - Account deletion MUST also delete or anonymize linked preference data.

16. Session Management & Auditing:

    - Session identifiers MUST be random, 128-bit entropy minimum, and stored
      only in memory (or OS keyring when headless automation requires).
    - Audit log retention for identity events MUST be ≥ 365 days. Log entries
      MUST include username, actor, action (`login_success`, `login_failure`,
      `reset`, `unblock`, `logout`), and correlation IDs.
    - Automated anomaly detection MUST flag >10 failed attempts/day/user and
      escalate to maintainers.

17. Lockout Prevention (Always-Available Accounts):

    - The system MUST provision two always-available accounts (one `dev`, one
      `admin`) during database initialization.
    - These accounts MUST NOT be deletable or deactivatable via standard
      UI/CLI/API flows; removal requires direct database modification with
      audit trail.
    - Password initialization MUST occur via secure operator procedure, never
      hard-coded defaults.
    - Implementation MUST include an `is_protected` flag on user records to
      enforce deletion/deactivation guards.

18. Break-Glass Emergency Access:

    - The system MUST provision two break-glass accounts (one `dev`, one
      `admin`) that are disabled by default.
    - Enablement MUST require an explicit CLI flag or environment variable;
      break-glass accounts MUST NOT be accessible through normal login flows
      when disabled.
    - Credentials MUST be stored offline (sealed envelope, hardware security
      module, or equivalent) and MUST NOT exist in version control or config.
    - Successful break-glass login MUST emit an immediate alert to all active
      admin accounts and create a high-priority audit entry.
    - Post-use password rotation MUST be enforced; the system SHOULD block
      further break-glass operations until rotation completes.
    - Annual drill: break-glass credentials MUST be tested at least once per
      year with documented results.

19. Role Taxonomy & Privilege Escalation:

    - The system enforces four roles: `dev`, `admin`, `user`, `readonly`.
    - New accounts MUST default to `pending` status until approved by an admin.
    - Role escalation (e.g., `user` → `admin`) MUST require admin approval and
      emit an audit entry with before/after roles.
    - Role demotion MAY occur without approval but MUST still emit audit.
    - `readonly` accounts MUST be blocked from any destructive file operation
      (delete, move, sync with overwrite, secure wipe) regardless of feature
      flags.

## Development Workflow & Quality Gates

1. Branching: feature/_, fix/_, chore/_, docs/_ naming. One logical change per
   PR. PR description MUST map changes to affected principles (checklist).
2. TDD Flow: Write failing tests → implement → refactor with green tests.
3. Reviews: Minimum 2 maintainer approvals for: destructive engine changes,
   security-sensitive code, tool discovery system changes, or performance-critical
   paths; otherwise ≥ 1.
4. Static Analysis: Lint (flake8/black), mypy, security scanning (bandit or
   equivalent) MUST pass before review request.
5. Release Process: Semantic Versioning (SemVer). Automated CI builds assets
   (binaries / PyPI wheel) after tag push. Changelog entry REQUIRED.
6. Documentation Gate: PR adding/changing user-visible behavior MUST update
   user guide + API reference before merge.
7. Test Categories: Unit (fast, isolated), Integration (engines, DB, FS), GUI
   smoke (launch, open representative tools, validate tool class imports),
   Performance (nightly), Security (pattern scans). Critical regressions block
   release.
8. Incident Handling: Production-impacting defect (data loss, security) MUST
   trigger post-mortem within 72h including root cause, principle impacts, and
   remediation tasks.
9. Artifact Retention: Build + test logs retained ≥ 180 days for audit.
10. Contribution Onboarding: New contributor PR triggers automated checklist
    comment with principle summary and required gates.

11. Preference Layer Gates:

    - New/changed preferences MUST include: type, default, validation, and doc.
    - Preference migrations MUST have unit + integration tests and rollback
      guidance.
    - Theming changes MUST pass accessibility checks and visual smoke tests.

12. Authentication Compliance:

    - Features touching identity MUST list Principle VII impacts in PRs.
    - Login UI/CLI changes MUST include manual verification steps + screenshots
      or recordings.
    - Automated tests MUST exercise happy path, lockout, reset, and audit
      logging before merge.

## Governance

1. Authority: This Constitution supersedes conflicting informal practices.
2. Amendment Proposal: Open a PR modifying this file plus a justification
   section in description referencing impacted principles and rationale.
3. Approval Requirements: Minor & Patch: ≥ 2 maintainer approvals. Major
   (adding/removing/redefining a principle or changing governance mechanics):
   ≥ 3 maintainer approvals + migration strategy document.
4. Versioning Policy (Governance Doc):
   - MAJOR: Backward-incompatible governance change; principle removal or
     semantic redefinition.
   - MINOR: New principle, new mandatory gate, or material expansion of a
     principle's normative rules.
   - PATCH: Clarifications, typo fixes, non-normative wording, formatting.
5. Compliance Review: Quarterly audit (end of Mar/Jun/Sep/Dec) produces a
   report listing deviations + corrective actions tracked as issues.
6. Deprecation Cycle: Announce deprecated public API in CHANGELOG with target
   removal version; MUST supply migration guidance.
7. Data & Preference Migrations: Any breaking change to preference categories,
   keys, or types MUST ship with a migration plan, automated migration script,
   and fallback defaults. Cross-module migrations MUST not introduce coupling;
   each module owns its scope.
8. Emergency Amendments: Security/data-loss critical changes may bypass
   normal cycle with expedited review (≥ 2 approvals) then retroactive audit.
9. Enforcement: Every PR template MUST include a "Constitution Compliance"
   checklist; reviewers MUST block until all mandatory gates pass.
10. Ratification: This initial version (1.0.0) is ratified by founding
    maintainers on the date below. Future amendments update Last Amended.
11. Dispute Resolution: If reviewers deadlock, escalate to maintainer vote; a
    simple majority decides within 5 business days.

**Version**: 1.3.0 | **Ratified**: 2025-09-29 | **Last Amended**: 2025-11-26
