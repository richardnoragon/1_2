# Research: Login & Password Integration Upgrade — Lockout Prevention

**Feature**: 007-upgrade-to-login  
**Date**: 2025-11-26  
**Status**: Complete

---

## Research Summary

This document consolidates research findings for the lockout prevention upgrade. All Technical Context items have been resolved with no remaining NEEDS CLARIFICATION markers.

---

## 1. Always-Available Account Protection Patterns

### Decision

Use database-level `is_always_available` flag with application-layer enforcement guards in services.

### Rationale

- Flag-based approach keeps the schema simple while allowing service-layer deletion guards
- Single table query can identify all protected accounts
- Application layer can provide descriptive error messages when protection is triggered
- Aligns with existing `UserAccount` model extension patterns from 006-baseline

### Alternatives Considered

| Alternative                             | Why Rejected                                                      |
| --------------------------------------- | ----------------------------------------------------------------- |
| Separate `protected_accounts` table     | Adds join complexity, harder to query account status in one query |
| Database-level trigger for deletion     | Less portable across SQLite/PostgreSQL, harder to test            |
| Config file list of protected usernames | Decoupled from DB state, can drift, harder to audit               |

### Implementation Notes

- Add `is_always_available BOOLEAN DEFAULT FALSE` to `user_accounts`
- Service layer checks flag before delete/disable operations
- Bootstrap service sets flag during initial provisioning
- Flag cannot be modified via normal account management interfaces

---

## 2. Break-Glass Credential Storage

### Decision

Credentials stored offline (sealed envelope or secure vault), access enabled via explicit CLI flag or environment variable.

### Rationale

- Offline storage prevents accidental break-glass usage during routine operations
- CLI flag (`--enable-break-glass`) creates explicit operator intent
- Environment variable (`RFU_ENABLE_BREAK_GLASS=true`) supports automation scenarios
- Matches industry best practices for emergency access patterns

### Alternatives Considered

| Alternative                           | Why Rejected                                                        |
| ------------------------------------- | ------------------------------------------------------------------- |
| Always-enabled with strong passwords  | Too easy to misuse for routine operations, dilutes emergency intent |
| Database-stored encrypted credentials | Defeats purpose if DB is compromised                                |
| Hardware security module only         | Overkill for desktop application, adds deployment complexity        |

### Implementation Notes

- Bootstrap generates credentials and exports via:
  1. Console output (for immediate operator copy)
  2. Secure note file in configurable directory
- Accounts marked `is_break_glass=true` are disabled by default
- Login flow checks for enablement flag before authenticating break-glass accounts
- Usage triggers enhanced audit logging and password rotation

---

## 3. Auto-Unblock Mechanism for Always-Available Accounts

### Decision

5-minute cooldown with timestamp tracking in `AlwaysAvailableAccountConfig` table, auto-unblock after cooldown expires.

### Rationale

- Balances security (lockout still triggers on brute-force attempts) with availability (auto-recovery)
- Prevents permanent lockout of emergency accounts
- Cooldown is configurable per-account for flexibility
- Timestamp-based approach works without background workers

### Alternatives Considered

| Alternative                   | Why Rejected                                 |
| ----------------------------- | -------------------------------------------- |
| Permanent immunity to lockout | Reduces security against brute-force attacks |
| Immediate auto-unblock        | No protection against active attacks         |
| Manual-only unblock           | Defeats purpose of always-available accounts |

### Implementation Notes

- `AlwaysAvailableAccountConfig` tracks:
  - `last_cooldown_start`: When lockout was triggered
  - `cooldown_duration_minutes`: Configurable (default 5)
  - `auto_unblock_enabled`: Can be disabled if needed
- Login flow checks if cooldown has expired and auto-unblocks
- Audit logs capture both lockout and auto-unblock events

---

## 4. Role Migration from 006-baseline

### Decision

Rename `standard` → `user`, add `dev` and `readonly` roles to create four-tier hierarchy.

### Rationale

- `user` is clearer and more universally understood than `standard`
- `dev` role provides debugging/diagnostic access separate from admin
- `readonly` role enables view-only access for auditors, observers
- Four-tier hierarchy matches constitution v1.3.0 requirements (§VII Role Taxonomy)

### Alternatives Considered

| Alternative                       | Why Rejected                                          |
| --------------------------------- | ----------------------------------------------------- |
| Keep `standard` name              | Confusing terminology, doesn't convey privilege level |
| Three roles (admin/user/readonly) | No separation for debugging access                    |
| Five+ roles                       | Overcomplicated for desktop application               |

### Migration Strategy

1. Add new role enum values (`dev`, `readonly`)
2. Update existing `standard` records to `user` via migration script
3. Preserve `admin` records unchanged
4. Bootstrap creates protected `dev` and `admin` accounts

---

## 5. Break-Glass Audit Enhancement

### Decision

Create dedicated `BreakGlassUsageLog` table with comprehensive session tracking, separate from general `AdminActionAudit`.

### Rationale

- Break-glass usage has different retention requirements (may need longer)
- Specialized reporting needs (who, when, why, what actions)
- Session-level tracking (login to logout) vs. action-level logging
- Easier to query for compliance reporting

### Alternatives Considered

| Alternative                                        | Why Rejected                                         |
| -------------------------------------------------- | ---------------------------------------------------- |
| Extend `AdminActionAudit` with break-glass columns | Muddies general audit with specialized data          |
| Log file only                                      | Harder to query, no structured reporting             |
| Single audit table with type discriminator         | Complicates queries for break-glass specific reports |

### Schema Design

```sql
CREATE TABLE break_glass_usage_log (
    id INTEGER PRIMARY KEY,
    session_id TEXT NOT NULL,
    account_username TEXT NOT NULL,
    login_timestamp TEXT NOT NULL,
    logout_timestamp TEXT,
    justification TEXT NOT NULL,
    actions_performed TEXT,  -- JSON array
    post_usage_rotation_status TEXT DEFAULT 'pending'
);
```

---

## 6. Lockout Prevention Invariant

### Decision

System maintains invariant: "At least one administrative path to the system is always accessible."

### Rationale

- Prevents complete lockout scenarios
- Constitution v1.3.0 §VII explicitly requires this guarantee
- Multiple fallback paths (always-available → break-glass → direct DB rescue)

### Enforcement Mechanism

1. **Always-Available Accounts**: Two accounts (dev + admin) with auto-unblock
2. **Break-Glass Accounts**: Two emergency accounts (dev + admin) with offline credentials
3. **Cross-Recovery**: If always-available is locked, break-glass can unblock it
4. **Direct DB Rescue**: Last resort via rescue.py script (documented in fleeting notes)

### Invariant Verification

- Health check queries:
  - At least one always-available account exists and is not permanently blocked
  - Break-glass accounts exist and credentials are rotated within policy
- CLI command: `rfu_admin.py health-check --lockout-prevention`

---

## Dependencies Confirmed

| Dependency  | Version | Purpose                     |
| ----------- | ------- | --------------------------- |
| argon2-cffi | ≥21.0.0 | Password hashing (existing) |
| PyQt5       | ≥5.15.0 | GUI framework (existing)    |
| sqlite3     | stdlib  | Database (existing)         |
| pytest      | ≥7.0.0  | Testing (existing)          |

---

## References

- 006-baseline-login-password spec.md
- 005-Login and Password Integration fleeting notes
- Constitution v1.3.0 (§VII Identity & Access Control)
- OWASP Break-Glass Account Guidelines

---

**Research Complete**: All unknowns resolved, ready for Phase 1 design.
