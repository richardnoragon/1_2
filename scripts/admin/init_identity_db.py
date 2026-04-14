#!/usr/bin/env python3
"""Initialize the RFU identity database with the full extended schema.

This script is idempotent — safe to run multiple times.  It creates
``src/data/rfu_identity.sqlite3`` (or the path given via ``--database-path``)
with all tables required by the authentication system, including the
007‑upgrade-to-login extensions (always-available and break-glass columns).

Usage:
    python scripts/admin/init_identity_db.py
    python scripts/admin/init_identity_db.py --database-path /custom/path.db
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Full schema DDL (single source of truth — includes all 006+007 columns)
# ---------------------------------------------------------------------------
_SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys = ON;

-- ================================================================
-- USER ACCOUNTS  (006 base + 007 extension columns)
-- ================================================================
CREATE TABLE IF NOT EXISTS user_accounts (
    username TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    password_salt BLOB NOT NULL,
    role TEXT NOT NULL DEFAULT 'user' CHECK (
        role IN ('dev', 'admin', 'user', 'standard', 'readonly')
    ),
    account_status TEXT NOT NULL DEFAULT 'pending' CHECK (
        account_status IN ('pending', 'active', 'blocked', 'disabled')
    ),
    is_blocked INTEGER NOT NULL DEFAULT 0 CHECK (is_blocked IN (0, 1)),
    login_attempts INTEGER NOT NULL DEFAULT 0 CHECK (login_attempts >= 0),
    last_login TEXT,
    last_failed_login TEXT,
    preferences_id TEXT,
    share_preferences INTEGER NOT NULL DEFAULT 0 CHECK (share_preferences IN (0, 1)),
    registration_channel TEXT NOT NULL DEFAULT 'hub' CHECK (
        registration_channel IN ('hub', 'cli', 'gui', 'bootstrap')
    ),
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
    -- 007 lockout-prevention extensions
    is_always_available INTEGER NOT NULL DEFAULT 0 CHECK (is_always_available IN (0, 1)),
    is_break_glass INTEGER NOT NULL DEFAULT 0 CHECK (is_break_glass IN (0, 1)),
    break_glass_justification TEXT,
    auto_unblock_at TEXT,
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
CREATE INDEX IF NOT EXISTS idx_user_accounts_always_available ON user_accounts(is_always_available);
CREATE INDEX IF NOT EXISTS idx_user_accounts_break_glass ON user_accounts(is_break_glass);

-- ================================================================
-- MFA RECOVERY CODES
-- ================================================================
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
-- SESSION TOKENS  (006 base + 007 session_type / usage_log_id)
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
    session_type TEXT NOT NULL DEFAULT 'standard'
        CHECK (session_type IN ('standard', 'break_glass', 'always_available')),
    usage_log_id TEXT,
    FOREIGN KEY(user_id) REFERENCES user_accounts(username) ON DELETE CASCADE,
    FOREIGN KEY(preferences_id)
        REFERENCES user_preferences(preferences_id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_session_tokens_user_id ON session_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_session_tokens_revoked ON session_tokens(revoked);
CREATE INDEX IF NOT EXISTS idx_session_tokens_expires_at ON session_tokens(expires_at);
CREATE INDEX IF NOT EXISTS idx_session_tokens_preferences_id ON session_tokens(preferences_id);
CREATE INDEX IF NOT EXISTS idx_session_tokens_session_type ON session_tokens(session_type);

-- ================================================================
-- RESET REQUESTS
-- ================================================================
CREATE TABLE IF NOT EXISTS reset_requests (
    request_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    initiated_by TEXT NOT NULL,
    reason TEXT,
    origin_surface TEXT NOT NULL CHECK (origin_surface IN ('gui', 'cli', 'service')),
    dispatcher_channel TEXT NOT NULL CHECK (
        dispatcher_channel IN ('console', 'secure_note', 'cli')
    ),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (
        status IN ('pending', 'delivered', 'completed', 'expired', 'cancelled')
    ),
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
-- ADMIN ACTION AUDIT  (006 base + 007 action types)
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
            'self_registration',
            'break_glass_login',
            'break_glass_logout',
            'break_glass_action',
            'always_available_cooldown',
            'trigger_cooldown',
            'account_bootstrap'
        )
    ),
    origin_surface TEXT NOT NULL CHECK (origin_surface IN ('gui', 'cli', 'service')),
    details TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    correlation_id TEXT,
    metadata TEXT,
    FOREIGN KEY(actor_username) REFERENCES user_accounts(username),
    FOREIGN KEY(target_username)
        REFERENCES user_accounts(username) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_admin_action_created_at ON admin_action_audit(created_at);
CREATE INDEX IF NOT EXISTS idx_admin_action_actor ON admin_action_audit(actor_username);
CREATE INDEX IF NOT EXISTS idx_admin_action_target ON admin_action_audit(target_username);
CREATE INDEX IF NOT EXISTS idx_admin_action_type ON admin_action_audit(action_type);
CREATE INDEX IF NOT EXISTS idx_admin_action_origin ON admin_action_audit(origin_surface);

-- ================================================================
-- PENDING PREFERENCE ALERTS
-- ================================================================
CREATE TABLE IF NOT EXISTS pending_preference_alerts (
    alert_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    detected_at TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    resolution_state TEXT NOT NULL DEFAULT 'open' CHECK (
        resolution_state IN ('open', 'investigating', 'resolved', 'dismissed')
    ),
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
-- BREAK-GLASS USAGE LOG  (007 new table)
-- ================================================================
CREATE TABLE IF NOT EXISTS break_glass_usage_log (
    log_id TEXT PRIMARY KEY,
    account_username TEXT NOT NULL,
    session_id TEXT,
    justification TEXT NOT NULL,
    activated_at TEXT NOT NULL DEFAULT (datetime('now')),
    deactivated_at TEXT,
    actor_ip TEXT,
    actions_performed INTEGER NOT NULL DEFAULT 0,
    metadata TEXT,
    FOREIGN KEY(account_username)
        REFERENCES user_accounts(username) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_bg_usage_log_username
    ON break_glass_usage_log(account_username);
CREATE INDEX IF NOT EXISTS idx_bg_usage_log_activated
    ON break_glass_usage_log(activated_at);

-- ================================================================
-- ADMIN NOTIFICATIONS  (007 new table)
-- ================================================================
CREATE TABLE IF NOT EXISTS admin_notifications (
    notification_id TEXT PRIMARY KEY,
    notification_type TEXT NOT NULL CHECK (
        notification_type IN (
            'break_glass_usage',
            'lockout_prevented',
            'failed_login_spike',
            'account_bootstrap',
            'credential_rotation'
        )
    ),
    target_username TEXT,
    message TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'info' CHECK (
        severity IN ('info', 'warning', 'critical')
    ),
    acknowledged INTEGER NOT NULL DEFAULT 0 CHECK (acknowledged IN (0, 1)),
    acknowledged_at TEXT,
    acknowledged_by TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    metadata TEXT
);

CREATE INDEX IF NOT EXISTS idx_admin_notifications_type
    ON admin_notifications(notification_type);
CREATE INDEX IF NOT EXISTS idx_admin_notifications_created
    ON admin_notifications(created_at);
CREATE INDEX IF NOT EXISTS idx_admin_notifications_acked
    ON admin_notifications(acknowledged);

-- ================================================================
-- ALWAYS-AVAILABLE ACCOUNT CONFIG  (007 new table)
-- ================================================================
CREATE TABLE IF NOT EXISTS always_available_account_config (
    config_id TEXT PRIMARY KEY DEFAULT 'singleton',
    cooldown_minutes INTEGER NOT NULL DEFAULT 15
        CHECK (cooldown_minutes BETWEEN 1 AND 1440),
    max_consecutive_failures INTEGER NOT NULL DEFAULT 5
        CHECK (max_consecutive_failures BETWEEN 1 AND 100),
    auto_unblock_enabled INTEGER NOT NULL DEFAULT 1 CHECK (auto_unblock_enabled IN (0, 1)),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_by TEXT,
    notes TEXT
);

INSERT OR IGNORE INTO always_available_account_config
    (config_id, cooldown_minutes, max_consecutive_failures, auto_unblock_enabled)
VALUES ('singleton', 15, 5, 1);

-- ================================================================
-- SCHEMA VERSIONING
-- ================================================================
CREATE TABLE IF NOT EXISTS rfu_schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL,
    description TEXT
);

INSERT OR REPLACE INTO rfu_schema_version (version, applied_at, description)
VALUES (7, datetime('now'), 'Full identity schema with 007 lockout-prevention extensions');
"""


def init_database(db_path: Path, *, verbose: bool = True) -> None:
    """Create the identity database at *db_path* with the full schema."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    existed = db_path.exists()

    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(_SCHEMA_SQL)
        conn.commit()
    finally:
        conn.close()

    if verbose:
        action = "Updated" if existed else "Created"
        print(f"{action} identity database: {db_path}")
        print("Schema version 7 applied (006 + 007 lockout-prevention extensions).")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialise the RFU identity SQLite database."
    )
    parser.add_argument(
        "--database-path",
        default=None,
        help=(
            "Path to the SQLite identity database to create/update. "
            "Defaults to src/data/rfu_identity.sqlite3 relative to the "
            "project root."
        ),
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress informational output.",
    )
    return parser.parse_args()


def _default_db_path() -> Path:
    # Resolve relative to this script (scripts/admin/) → project root
    project_root = Path(__file__).resolve().parents[2]
    return project_root / "src" / "data" / "rfu_identity.sqlite3"


def main() -> int:
    args = _parse_args()
    db_path = Path(args.database_path) if args.database_path else _default_db_path()
    try:
        init_database(db_path, verbose=not args.quiet)
    except Exception as exc:  # pylint: disable=broad-except
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
