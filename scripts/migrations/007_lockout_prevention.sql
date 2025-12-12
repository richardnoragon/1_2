-- Migration: 007_lockout_prevention.sql
-- Purpose: Add four-role system and lockout prevention features
-- Spec: specs/007-upgrade-to-login/spec.md
-- Date: 2025-11-26

-- ===========================================================================
-- PHASE 1: Extend user_accounts table for lockout prevention
-- ===========================================================================

-- Add lockout prevention columns to user_accounts
ALTER TABLE user_accounts ADD COLUMN is_always_available INTEGER DEFAULT 0;
ALTER TABLE user_accounts ADD COLUMN is_break_glass INTEGER DEFAULT 0;
ALTER TABLE user_accounts ADD COLUMN break_glass_justification TEXT;
ALTER TABLE user_accounts ADD COLUMN auto_unblock_at TEXT;

-- ===========================================================================
-- PHASE 2: Migrate standard role to user role
-- ===========================================================================

-- Update existing 'standard' roles to 'user'
UPDATE user_accounts SET role = 'user' WHERE role = 'standard';

-- ===========================================================================
-- PHASE 3: Extend session_tokens table for break-glass tracking
-- ===========================================================================

ALTER TABLE session_tokens ADD COLUMN session_type TEXT DEFAULT 'normal';
ALTER TABLE session_tokens ADD COLUMN usage_log_id INTEGER;

-- ===========================================================================
-- PHASE 4: Create always_available_account_config table
-- ===========================================================================

CREATE TABLE IF NOT EXISTS always_available_account_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    last_cooldown_start TEXT,
    cooldown_duration_minutes INTEGER DEFAULT 5,
    auto_unblock_enabled INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (username) REFERENCES user_accounts(username) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_aa_config_username
    ON always_available_account_config(username);

-- ===========================================================================
-- PHASE 5: Create break_glass_usage_log table
-- ===========================================================================

CREATE TABLE IF NOT EXISTS break_glass_usage_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    account_username TEXT NOT NULL,
    login_timestamp TEXT NOT NULL,
    logout_timestamp TEXT,
    justification TEXT NOT NULL,
    actions_performed TEXT DEFAULT '[]',  -- JSON array
    post_usage_rotation_status TEXT DEFAULT 'not_required',
    client_ip TEXT,
    client_hostname TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (account_username) REFERENCES user_accounts(username)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_bg_usage_session
    ON break_glass_usage_log(session_id);
CREATE INDEX IF NOT EXISTS idx_bg_usage_username
    ON break_glass_usage_log(account_username);
CREATE INDEX IF NOT EXISTS idx_bg_usage_login_time
    ON break_glass_usage_log(login_timestamp);
CREATE INDEX IF NOT EXISTS idx_bg_usage_rotation_pending
    ON break_glass_usage_log(post_usage_rotation_status)
    WHERE post_usage_rotation_status = 'pending';

-- ===========================================================================
-- PHASE 6: Create admin_notification table (for break-glass alerts)
-- ===========================================================================

CREATE TABLE IF NOT EXISTS admin_notification (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    notification_type TEXT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT,
    metadata TEXT,  -- JSON payload
    acknowledged INTEGER DEFAULT 0,
    acknowledged_by TEXT,
    acknowledged_at TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    expires_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_admin_notif_type
    ON admin_notification(notification_type);
CREATE INDEX IF NOT EXISTS idx_admin_notif_unack
    ON admin_notification(acknowledged)
    WHERE acknowledged = 0;

-- ===========================================================================
-- PHASE 7: Add indexes for protected account queries
-- ===========================================================================

CREATE INDEX IF NOT EXISTS idx_user_always_available
    ON user_accounts(is_always_available)
    WHERE is_always_available = 1;

CREATE INDEX IF NOT EXISTS idx_user_break_glass
    ON user_accounts(is_break_glass)
    WHERE is_break_glass = 1;

CREATE INDEX IF NOT EXISTS idx_user_protected
    ON user_accounts(is_always_available, is_break_glass)
    WHERE is_always_available = 1 OR is_break_glass = 1;

CREATE INDEX IF NOT EXISTS idx_user_auto_unblock
    ON user_accounts(auto_unblock_at)
    WHERE auto_unblock_at IS NOT NULL;

-- ===========================================================================
-- ROLLBACK GUIDANCE
-- ===========================================================================
/*
To rollback this migration:

1. Drop new tables:
   DROP TABLE IF EXISTS admin_notification;
   DROP TABLE IF EXISTS break_glass_usage_log;
   DROP TABLE IF EXISTS always_available_account_config;

2. Remove new indexes on user_accounts:
   DROP INDEX IF EXISTS idx_user_always_available;
   DROP INDEX IF EXISTS idx_user_break_glass;
   DROP INDEX IF EXISTS idx_user_protected;
   DROP INDEX IF EXISTS idx_user_auto_unblock;

3. For SQLite, recreate user_accounts without new columns:
   -- SQLite does not support DROP COLUMN, so you must:
   CREATE TABLE user_accounts_backup AS SELECT
       username, password_hash, password_salt, role, account_status,
       login_attempts, is_blocked, preferences_id, share_preferences,
       registration_channel, registration_metadata, created_at, activated_at,
       blocked_at, updated_at, last_login, last_failed_login,
       enforced_password_change, mfa_enabled, mfa_secret_encrypted,
       mfa_recovery_codes, mfa_enforced_at
   FROM user_accounts;
   DROP TABLE user_accounts;
   ALTER TABLE user_accounts_backup RENAME TO user_accounts;
   -- Recreate original indexes

4. Revert role migration:
   UPDATE user_accounts SET role = 'standard' WHERE role = 'user';

5. Drop session_tokens new columns (same SQLite workaround as above)
*/
