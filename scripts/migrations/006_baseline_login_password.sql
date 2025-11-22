-- Migration 006: Login & Password Baseline Schema
-- Establishes identity tables required by specs/006-baseline-login-password
-- Author: GitHub Copilot (Phase 3.1)
-- Notes: Future MFA columns/hooks will extend this file during Phase 3.4+

PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

-- ================================================================
-- USER ACCOUNTS
-- Canonical identity record with Argon2 hashes, role metadata, and
-- registration tracking. `is_blocked` mirrors the account_status state
-- for compatibility with existing tooling.
-- ================================================================
CREATE TABLE IF NOT EXISTS user_accounts (
    username TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    password_salt BLOB NOT NULL,
    role TEXT NOT NULL DEFAULT 'standard' CHECK (role IN ('admin', 'standard')),
    account_status TEXT NOT NULL DEFAULT 'pending' CHECK (account_status IN ('pending', 'active', 'blocked', 'disabled')),
    is_blocked INTEGER NOT NULL DEFAULT 0 CHECK (is_blocked IN (0, 1)),
    login_attempts INTEGER NOT NULL DEFAULT 0 CHECK (login_attempts >= 0),
    last_login TEXT,
    last_failed_login TEXT,
    preferences_id TEXT,
    share_preferences INTEGER NOT NULL DEFAULT 0 CHECK (share_preferences IN (0, 1)),
    registration_channel TEXT NOT NULL DEFAULT 'hub' CHECK (registration_channel IN ('hub', 'cli', 'gui', 'bootstrap')),
    registration_metadata TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    activated_at TEXT,
    blocked_at TEXT,
    updated_at TEXT,
    enforced_password_change INTEGER NOT NULL DEFAULT 0 CHECK (enforced_password_change IN (0, 1)),
    mfa_enabled INTEGER NOT NULL DEFAULT 0 CHECK (mfa_enabled IN (0, 1)),
    mfa_secret_encrypted BLOB,
    mfa_recovery_codes TEXT,
    mfa_enforced_at TEXT,
    CHECK(length(username) BETWEEN 3 AND 128)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_user_accounts_preferences_id
    ON user_accounts(preferences_id)
    WHERE preferences_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_user_accounts_role ON user_accounts(role);
CREATE INDEX IF NOT EXISTS idx_user_accounts_status ON user_accounts(account_status);
CREATE INDEX IF NOT EXISTS idx_user_accounts_blocked ON user_accounts(is_blocked);
CREATE INDEX IF NOT EXISTS idx_user_accounts_login_attempts ON user_accounts(login_attempts);
CREATE INDEX IF NOT EXISTS idx_user_accounts_share_flag ON user_accounts(share_preferences);
CREATE INDEX IF NOT EXISTS idx_user_accounts_created_at ON user_accounts(created_at);
CREATE INDEX IF NOT EXISTS idx_user_accounts_mfa_enabled ON user_accounts(mfa_enabled);
CREATE INDEX IF NOT EXISTS idx_user_accounts_mfa_enforced_at ON user_accounts(mfa_enforced_at);

-- Recovery codes table keeps hashed codes for auditing + revocation.
CREATE TABLE IF NOT EXISTS user_mfa_recovery_codes (
    code_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    code_hash TEXT NOT NULL,
    issued_at TEXT NOT NULL DEFAULT (datetime('now')),
    redeemed_at TEXT,
    revoked_at TEXT,
    metadata TEXT,
    FOREIGN KEY(user_id) REFERENCES user_accounts(username) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_user_mfa_codes_user_id ON user_mfa_recovery_codes(user_id);
CREATE INDEX IF NOT EXISTS idx_user_mfa_codes_redeemed ON user_mfa_recovery_codes(redeemed_at);

-- ================================================================
-- USER PREFERENCES
-- Namespaced personalization bundle linked to a user once activated.
-- ================================================================
CREATE TABLE IF NOT EXISTS user_preferences (
    preferences_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    schema_version INTEGER NOT NULL DEFAULT 1,
    payload TEXT NOT NULL,
    is_encrypted INTEGER NOT NULL DEFAULT 0 CHECK (is_encrypted IN (0, 1)),
    metadata TEXT,
    shared_metadata TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY(user_id) REFERENCES user_accounts(username) ON DELETE CASCADE,
    UNIQUE(user_id)
);

CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_user_preferences_schema_version ON user_preferences(schema_version);
CREATE INDEX IF NOT EXISTS idx_user_preferences_updated_at ON user_preferences(updated_at);

-- ================================================================
-- SESSION TOKENS
-- Tracks GUI/CLI sessions using hashed handles for revocation.
-- ================================================================
CREATE TABLE IF NOT EXISTS session_tokens (
    session_handle_hash TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    issued_at TEXT NOT NULL,
    last_activity_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    surface TEXT NOT NULL CHECK (surface IN ('gui', 'cli')),
    origin_host TEXT,
    revoked INTEGER NOT NULL DEFAULT 0 CHECK (revoked IN (0, 1)),
    revoked_at TEXT,
    preferences_id TEXT,
    idle_timeout_deadline TEXT,
    FOREIGN KEY(user_id) REFERENCES user_accounts(username) ON DELETE CASCADE,
    FOREIGN KEY(preferences_id) REFERENCES user_preferences(preferences_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_session_tokens_user_id ON session_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_session_tokens_revoked ON session_tokens(revoked);
CREATE INDEX IF NOT EXISTS idx_session_tokens_expires_at ON session_tokens(expires_at);
CREATE INDEX IF NOT EXISTS idx_session_tokens_preferences_id ON session_tokens(preferences_id);

-- ================================================================
-- RESET REQUESTS
-- Captures admin-triggered reset workflows and dispatcher metadata.
-- ================================================================
CREATE TABLE IF NOT EXISTS reset_requests (
    request_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    initiated_by TEXT NOT NULL,
    reason TEXT,
    origin_surface TEXT NOT NULL CHECK (origin_surface IN ('gui', 'cli', 'service')),
    dispatcher_channel TEXT NOT NULL CHECK (dispatcher_channel IN ('console', 'secure_note', 'cli')),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'delivered', 'completed', 'expired', 'cancelled')),
    temporary_secret BLOB,
    secret_nonce BLOB,
    secret_displayed_at TEXT,
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at TEXT,
    justification TEXT,
    FOREIGN KEY(user_id) REFERENCES user_accounts(username) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_reset_requests_user_id ON reset_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_reset_requests_status ON reset_requests(status);
CREATE INDEX IF NOT EXISTS idx_reset_requests_expires_at ON reset_requests(expires_at);
CREATE INDEX IF NOT EXISTS idx_reset_requests_initiated_by ON reset_requests(initiated_by);

-- ================================================================
-- ADMIN ACTION AUDIT
-- Append-only ledger for approvals, resets, unblocks, preference exports.
-- ================================================================
CREATE TABLE IF NOT EXISTS admin_action_audit (
    audit_id TEXT PRIMARY KEY,
    actor_username TEXT NOT NULL,
    target_username TEXT,
    action_type TEXT NOT NULL CHECK (
        action_type IN (
            'approve_user',
            'reset_password',
            'unblock_user',
            'export_preferences',
            'login_success',
            'login_failure',
            'lockout',
            'share_preferences',
            'unauthorized_admin_action',
            'self_registration'
        )
    ),
    origin_surface TEXT NOT NULL CHECK (origin_surface IN ('gui', 'cli', 'service')),
    details TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    correlation_id TEXT,
    metadata TEXT,
    FOREIGN KEY(actor_username) REFERENCES user_accounts(username),
    FOREIGN KEY(target_username) REFERENCES user_accounts(username) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_admin_action_created_at ON admin_action_audit(created_at);
CREATE INDEX IF NOT EXISTS idx_admin_action_actor ON admin_action_audit(actor_username);
CREATE INDEX IF NOT EXISTS idx_admin_action_target ON admin_action_audit(target_username);
CREATE INDEX IF NOT EXISTS idx_admin_action_type ON admin_action_audit(action_type);
CREATE INDEX IF NOT EXISTS idx_admin_action_origin ON admin_action_audit(origin_surface);

-- ================================================================
-- PENDING PREFERENCE ALERTS
-- Flags preference corruption/remediation workflow states.
-- ================================================================
CREATE TABLE IF NOT EXISTS pending_preference_alerts (
    alert_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    detected_at TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    resolution_state TEXT NOT NULL DEFAULT 'open' CHECK (resolution_state IN ('open', 'investigating', 'resolved', 'dismissed')),
    notes TEXT,
    resolved_at TEXT,
    resolved_by TEXT,
    preference_snapshot_version INTEGER,
    metadata TEXT,
    FOREIGN KEY(user_id) REFERENCES user_accounts(username) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_preference_alerts_user_id ON pending_preference_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_preference_alerts_state ON pending_preference_alerts(resolution_state);
CREATE INDEX IF NOT EXISTS idx_preference_alerts_severity ON pending_preference_alerts(severity);

-- ================================================================
-- SCHEMA VERSIONING
-- ================================================================
CREATE TABLE IF NOT EXISTS rfu_schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL,
    description TEXT
);

INSERT OR REPLACE INTO rfu_schema_version (version, applied_at, description)
VALUES (6, datetime('now'), 'Login & password baseline identity schema');

-- Rollback guidance (manual):
-- 1. DROP TABLE IF EXISTS user_mfa_recovery_codes;
-- 2. Recreate user_accounts without the MFA columns using a temporary table:
--    a. ALTER TABLE user_accounts RENAME TO user_accounts_tmp;
--    b. Recreate user_accounts minus the MFA columns.
--    c. INSERT INTO new table selecting shared columns from user_accounts_tmp;
--    d. DROP TABLE user_accounts_tmp;
-- 3. Recreate indexes as needed. Perform these steps only if MFA has not been enabled
--    for any production users to avoid data loss of secrets.

COMMIT;
