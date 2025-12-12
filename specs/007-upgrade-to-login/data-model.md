# Data Model: Login & Password Integration Upgrade — Lockout Prevention

**Feature**: 007-upgrade-to-login  
**Date**: 2025-11-26  
**Status**: Complete

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                           user_accounts                              │
├─────────────────────────────────────────────────────────────────────┤
│ username (PK)           │ TEXT NOT NULL UNIQUE                       │
│ password_hash           │ TEXT NOT NULL                              │
│ role                    │ TEXT NOT NULL CHECK (dev|admin|user|readonly)│
│ account_status          │ TEXT NOT NULL CHECK (pending|active|blocked|disabled)│
│ is_always_available     │ BOOLEAN DEFAULT FALSE                      │
│ is_break_glass          │ BOOLEAN DEFAULT FALSE                      │
│ break_glass_justification│ TEXT                                      │
│ preferences_id          │ INTEGER → user_preferences.id              │
│ login_attempts          │ INTEGER DEFAULT 0                          │
│ is_blocked              │ BOOLEAN DEFAULT FALSE                      │
│ last_login              │ TEXT (ISO datetime)                        │
│ last_failed_login       │ TEXT (ISO datetime)                        │
│ activated_at            │ TEXT (ISO datetime)                        │
│ created_at              │ TEXT (ISO datetime) NOT NULL               │
│ updated_at              │ TEXT (ISO datetime)                        │
└─────────────────────────────────────────────────────────────────────┘
         │
         │ 1:1
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   always_available_account_config                    │
├─────────────────────────────────────────────────────────────────────┤
│ username (PK, FK)       │ TEXT → user_accounts.username              │
│ last_cooldown_start     │ TEXT (ISO datetime)                        │
│ cooldown_duration_minutes│ INTEGER DEFAULT 5                         │
│ auto_unblock_enabled    │ BOOLEAN DEFAULT TRUE                       │
│ created_at              │ TEXT (ISO datetime) NOT NULL               │
│ updated_at              │ TEXT (ISO datetime)                        │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                           session_tokens                             │
├─────────────────────────────────────────────────────────────────────┤
│ session_id (PK)         │ TEXT NOT NULL UNIQUE                       │
│ username (FK)           │ TEXT → user_accounts.username              │
│ session_handle_hash     │ TEXT NOT NULL                              │
│ session_type            │ TEXT CHECK (normal|break_glass)            │
│ preferences_id          │ INTEGER → user_preferences.id              │
│ created_at              │ TEXT (ISO datetime) NOT NULL               │
│ last_activity           │ TEXT (ISO datetime)                        │
│ expires_at              │ TEXT (ISO datetime)                        │
│ revoked_at              │ TEXT (ISO datetime)                        │
└─────────────────────────────────────────────────────────────────────┘
         │
         │ 1:0..1 (for break_glass sessions)
         ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        break_glass_usage_log                         │
├─────────────────────────────────────────────────────────────────────┤
│ id (PK)                 │ INTEGER PRIMARY KEY AUTOINCREMENT          │
│ session_id (FK)         │ TEXT → session_tokens.session_id           │
│ account_username (FK)   │ TEXT → user_accounts.username              │
│ login_timestamp         │ TEXT (ISO datetime) NOT NULL               │
│ logout_timestamp        │ TEXT (ISO datetime)                        │
│ justification           │ TEXT NOT NULL                              │
│ actions_performed       │ TEXT (JSON array)                          │
│ post_usage_rotation_status│ TEXT CHECK (pending|completed|failed)    │
│ created_at              │ TEXT (ISO datetime) NOT NULL               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Entity Definitions

### UserAccount (Extended)

**Purpose**: Represents an individual operator with authentication credentials and role-based permissions.

**New Fields** (added to 006-baseline):

| Field                       | Type    | Constraints                                  | Description                            |
| --------------------------- | ------- | -------------------------------------------- | -------------------------------------- |
| `role`                      | TEXT    | NOT NULL, CHECK (dev\|admin\|user\|readonly) | Four-tier role hierarchy               |
| `is_always_available`       | BOOLEAN | DEFAULT FALSE                                | Protected from deletion/disabling      |
| `is_break_glass`            | BOOLEAN | DEFAULT FALSE                                | Emergency recovery account             |
| `break_glass_justification` | TEXT    | NULLABLE                                     | Required when break-glass login occurs |

**Validation Rules**:

- `username`: 3-50 characters, alphanumeric + underscore, unique
- `password_hash`: Argon2id hash (never plaintext)
- `role`: Must be one of: dev, admin, user, readonly
- `is_always_available` and `is_break_glass`: Mutually exclusive (an account is one or the other, not both)

**State Transitions**:

```
pending → active (admin approval)
active → blocked (5 failed logins)
blocked → active (admin unblock OR auto-unblock for always-available)
active → disabled (admin action, not allowed for always-available)
```

**Invariants**:

- Always-available accounts cannot be deleted or disabled
- Break-glass accounts cannot be used without enablement flag
- Role escalation requires admin/dev approval

---

### AlwaysAvailableAccountConfig

**Purpose**: Stores configuration for always-available account auto-unblock mechanism.

| Field                       | Type    | Constraints  | Description                         |
| --------------------------- | ------- | ------------ | ----------------------------------- |
| `username`                  | TEXT    | PK, FK       | References protected user_account   |
| `last_cooldown_start`       | TEXT    | NULLABLE     | When lockout cooldown started       |
| `cooldown_duration_minutes` | INTEGER | DEFAULT 5    | Cooldown period before auto-unblock |
| `auto_unblock_enabled`      | BOOLEAN | DEFAULT TRUE | Can be disabled if needed           |

**Validation Rules**:

- `username` must reference an account with `is_always_available=true`
- `cooldown_duration_minutes` must be ≥ 1

**Auto-Unblock Logic**:

```python
def should_auto_unblock(config: AlwaysAvailableAccountConfig) -> bool:
    if not config.auto_unblock_enabled:
        return False
    if config.last_cooldown_start is None:
        return False
    elapsed = datetime.now() - config.last_cooldown_start
    return elapsed >= timedelta(minutes=config.cooldown_duration_minutes)
```

---

### BreakGlassUsageLog

**Purpose**: Tracks every break-glass session with enhanced audit detail.

| Field                        | Type    | Constraints       | Description                        |
| ---------------------------- | ------- | ----------------- | ---------------------------------- |
| `id`                         | INTEGER | PK, AUTOINCREMENT | Unique log entry ID                |
| `session_id`                 | TEXT    | FK                | References session_tokens          |
| `account_username`           | TEXT    | FK                | Which break-glass account was used |
| `login_timestamp`            | TEXT    | NOT NULL          | When session started               |
| `logout_timestamp`           | TEXT    | NULLABLE          | When session ended                 |
| `justification`              | TEXT    | NOT NULL          | Why break-glass was needed         |
| `actions_performed`          | TEXT    | JSON array        | List of actions during session     |
| `post_usage_rotation_status` | TEXT    | CHECK             | pending, completed, or failed      |

**Validation Rules**:

- `justification` must be non-empty
- `post_usage_rotation_status` must be updated when session ends

**Actions Tracking**:

```json
{
  "actions_performed": [
    {
      "action": "unblock_user",
      "target": "alice",
      "timestamp": "2025-11-26T10:30:00Z"
    },
    {
      "action": "reset_password",
      "target": "bob",
      "timestamp": "2025-11-26T10:32:00Z"
    }
  ]
}
```

---

### SessionToken (Extended)

**Purpose**: Represents an active authenticated session.

**New Fields** (added to 006-baseline):

| Field          | Type | Constraints                 | Description                      |
| -------------- | ---- | --------------------------- | -------------------------------- |
| `session_type` | TEXT | CHECK (normal\|break_glass) | Distinguishes emergency sessions |

**Session Type Behavior**:

- `normal`: Standard session behavior
- `break_glass`: Enhanced logging, actions tracked in `break_glass_usage_log`

---

## Role Hierarchy

```
dev (highest)
  ├── All admin capabilities
  ├── Debugging/diagnostics access
  ├── Break-glass account management
  └── Always-available account management

admin
  ├── All user capabilities
  ├── User management (create, approve, reset, unblock)
  ├── Configuration management
  └── System logs access

user
  ├── All readonly capabilities
  ├── File operations (copy, move, delete, sync)
  └── Preference management

readonly (lowest)
  └── View-only access (no write operations)
```

---

## Protected Account Bootstrap

On database initialization, the following accounts are created:

| Username               | Role  | Type             | Purpose                  |
| ---------------------- | ----- | ---------------- | ------------------------ |
| `rfu_dev_always`       | dev   | always-available | Guaranteed dev access    |
| `rfu_admin_always`     | admin | always-available | Guaranteed admin access  |
| `rfu_dev_breakglass`   | dev   | break-glass      | Emergency dev recovery   |
| `rfu_admin_breakglass` | admin | break-glass      | Emergency admin recovery |

**Bootstrap Credentials**:

- Generated via secure random (32 bytes, base64 encoded)
- Displayed via console output for operator copy
- Exported to secure note file in configurable directory
- Must be changed on first login (enforced via flag)

---

## Migration from 006-baseline

### Schema Changes

```sql
-- Add new columns to user_accounts
ALTER TABLE user_accounts ADD COLUMN is_always_available BOOLEAN DEFAULT FALSE;
ALTER TABLE user_accounts ADD COLUMN is_break_glass BOOLEAN DEFAULT FALSE;
ALTER TABLE user_accounts ADD COLUMN break_glass_justification TEXT;

-- Update role enum (add dev, readonly; rename standard → user)
UPDATE user_accounts SET role = 'user' WHERE role = 'standard';

-- Add session_type to session_tokens
ALTER TABLE session_tokens ADD COLUMN session_type TEXT DEFAULT 'normal';

-- Create new tables
CREATE TABLE always_available_account_config (
    username TEXT PRIMARY KEY REFERENCES user_accounts(username),
    last_cooldown_start TEXT,
    cooldown_duration_minutes INTEGER DEFAULT 5,
    auto_unblock_enabled BOOLEAN DEFAULT TRUE,
    created_at TEXT NOT NULL,
    updated_at TEXT
);

CREATE TABLE break_glass_usage_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES session_tokens(session_id),
    account_username TEXT NOT NULL REFERENCES user_accounts(username),
    login_timestamp TEXT NOT NULL,
    logout_timestamp TEXT,
    justification TEXT NOT NULL,
    actions_performed TEXT,
    post_usage_rotation_status TEXT DEFAULT 'pending',
    created_at TEXT NOT NULL
);
```

### Data Migration

1. Existing `standard` role accounts → `user` role
2. Existing `admin` accounts remain unchanged
3. Bootstrap creates protected accounts (always-available + break-glass)

---

## Indexes

```sql
-- Fast lookup for protected accounts
CREATE INDEX idx_user_accounts_always_available ON user_accounts(is_always_available) WHERE is_always_available = TRUE;
CREATE INDEX idx_user_accounts_break_glass ON user_accounts(is_break_glass) WHERE is_break_glass = TRUE;

-- Break-glass audit queries
CREATE INDEX idx_break_glass_usage_log_username ON break_glass_usage_log(account_username);
CREATE INDEX idx_break_glass_usage_log_rotation ON break_glass_usage_log(post_usage_rotation_status) WHERE post_usage_rotation_status = 'pending';
```

---

**Data Model Complete**: Ready for contract generation.
