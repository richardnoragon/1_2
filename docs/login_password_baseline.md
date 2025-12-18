# Login & Password Baseline – Secure Reset + CLI Notes

The Phase 3.7 polish pass adds a hardened reset workflow around
`SecureSecretDispatcher`, refreshed CLI helpers, and documentation for MFA
readiness. Phase 3.8 adds lockout prevention with protected accounts.

---

## Four-Role Authorization System

The identity system uses a four-tier role hierarchy for authorization:

| Role       | Level    | Description                                             |
| ---------- | -------- | ------------------------------------------------------- |
| `dev`      | Highest  | Developer/superuser access, break-glass history viewing |
| `admin`    | High     | Administrative operations, user management, auditing    |
| `user`     | Standard | Normal application access                               |
| `readonly` | Lowest   | View-only access                                        |

**Role Hierarchy Rules:**

- Higher roles inherit all capabilities of lower roles
- Dev role is required for break-glass history viewing and diagnostic access
- Admin role is required for user management, password resets, and unblocking
- Role assignment requires admin or dev privileges

### Role Capability Matrix

The capability matrix defines which roles have access to specific features:

| Capability                | dev | admin | user | readonly |
| ------------------------- | --- | ----- | ---- | -------- |
| `VIEW_DATA`               | ✓   | ✓     | ✓    | ✓        |
| `MODIFY_DATA`             | ✓   | ✓     | ✓    | ✗        |
| `MANAGE_USERS`            | ✓   | ✓     | ✗    | ✗        |
| `MANAGE_CONFIG`           | ✓   | ✓     | ✗    | ✗        |
| `ACCESS_LOGS`             | ✓   | ✓     | ✗    | ✗        |
| `ACCESS_DEBUGGING`        | ✓   | ✗     | ✗    | ✗        |
| `MANAGE_BREAK_GLASS`      | ✓   | ✗     | ✗    | ✗        |
| `MANAGE_ALWAYS_AVAILABLE` | ✓   | ✗     | ✗    | ✗        |

**Capability Definitions:**

- `VIEW_DATA`: Read application data and user's own profile
- `MODIFY_DATA`: Create, update, delete application data
- `MANAGE_USERS`: Create, modify, delete user accounts; reset passwords
- `MANAGE_CONFIG`: Modify system configuration settings
- `ACCESS_LOGS`: View audit logs and system logs
- `ACCESS_DEBUGGING`: Access diagnostic tools and debug information
- `MANAGE_BREAK_GLASS`: View break-glass history, rotate credentials
- `MANAGE_ALWAYS_AVAILABLE`: Configure always-available account settings

### Role Escalation Rules

Role changes follow strict escalation rules:

1. **Cannot escalate above own role**: Admin cannot promote to dev
2. **Dev-only promotions**: Only dev role can promote to admin or dev
3. **Demotion always allowed**: Higher roles can demote lower roles
4. **Protected accounts immutable**: Cannot change role of protected accounts

**Examples:**

| Actor Role | Current Role | New Role | Allowed | Reason                        |
| ---------- | ------------ | -------- | ------- | ----------------------------- |
| dev        | user         | admin    | ✓       | Dev can escalate to admin     |
| dev        | user         | dev      | ✓       | Dev can escalate to dev       |
| admin      | user         | admin    | ✓       | Admin can escalate to admin   |
| admin      | user         | dev      | ✗       | Admin cannot escalate to dev  |
| user       | readonly     | user     | ✓       | User can escalate to user     |
| user       | readonly     | admin    | ✗       | User cannot escalate to admin |

---

## Lockout Prevention System (Phase 3.8)

### Overview

The lockout prevention system ensures administrators can never be completely
locked out of the system. It uses two types of protected accounts:

1. **Always-Available Accounts**: Cannot be blocked by failed login attempts
2. **Break-Glass Accounts**: Emergency access requiring justification

### Protected Account Types

| Account                | Role  | Type             | Purpose                            |
| ---------------------- | ----- | ---------------- | ---------------------------------- |
| `rfu_dev_always`       | dev   | always-available | Developer access that never blocks |
| `rfu_admin_always`     | admin | always-available | Admin access that never blocks     |
| `rfu_dev_breakglass`   | dev   | break-glass      | Emergency dev access               |
| `rfu_admin_breakglass` | admin | break-glass      | Emergency admin access             |

### Always-Available Accounts

Always-available accounts (`is_always_available=True`):

- **Cannot be blocked** by failed login attempts
- Login attempts are tracked but never trigger lockout
- Provide guaranteed access for routine administration
- Credentials should be kept secure and rotated periodically

### Break-Glass Accounts

Break-glass accounts (`is_break_glass=True`):

- **Emergency-only access** when all other accounts are blocked
- Require a **justification** (minimum 10 characters) at login
- All usage is **logged** with session ID, timestamp, and justification
- Credentials **must be rotated** after each use
- Subject to **automatic cooldown** to prevent abuse

### Break-Glass Login Flow

1. User attempts login with break-glass credentials
2. System detects break-glass account and raises `BreakGlassJustificationRequired`
3. Login dialog prompts for justification (minimum 10 characters)
4. Justification is logged to `break_glass_usage_log` table
5. Session is created with `session_type='break_glass'`
6. After logout, credentials should be rotated via CLI

### Automatic Cooldown Mechanism

When an always-available account is blocked:

1. System automatically schedules unblock (`auto_unblock_at` timestamp)
2. Default cooldown period: 30 minutes
3. After cooldown expires, account is auto-unblocked on next login attempt
4. Prevents permanent lockout while deterring brute-force attacks

---

## CLI Commands for Lockout Prevention

### Bootstrap Protected Accounts

Initialize the four protected accounts on a fresh or recovered system:

```bash
python scripts/admin/rfu_admin.py bootstrap-protected-accounts \
   --database-path <db> \
   [--show-console]        # Display passwords on console (default: True)
   [--no-show-console]     # Suppress console display
   [--export-credentials]  # Export to secure file (default: True)
```

- **Idempotent**: Safe to run multiple times
- Creates `protected_credentials/` directory with encrypted credentials
- Console output shows temporary passwords for initial setup

### List Protected Accounts

View status of all protected accounts:

```bash
python scripts/admin/rfu_admin.py list-protected-accounts \
   --database-path <db>
```

Returns JSON with:

- `complete`: Whether all 4 accounts exist
- `accounts`: List with username, role, type, status, is_blocked
- `missing`: List of accounts not yet created

### Rotate Break-Glass Credentials

Rotate credentials after break-glass usage:

```bash
python scripts/admin/rfu_admin.py rotate-break-glass \
   --database-path <db> \
   --username <rfu_dev_breakglass|rfu_admin_breakglass> \
   [--show-console]        # Display new password (default: True)
   [--no-show-console]     # Suppress display
   [--export-credentials]  # Export to file (default: True)
```

- Must be run after each break-glass login
- Generates new secure random password
- Resets login attempts and blocked state
- Creates audit trail entry

### Unblock User

Manually unblock any user (including protected accounts):

```bash
python scripts/admin/rfu_admin.py unblock-user \
   --database-path <db> \
   --username <user> \
   --justification "<reason>"
```

---

## Disaster Recovery Procedures

### Complete Lockout Recovery

If all administrator accounts are locked out:

1. **Bootstrap** (if protected accounts don't exist):

   ```bash
   python scripts/admin/rfu_admin.py bootstrap-protected-accounts \
      --database-path <db> --export-credentials
   ```

2. **List** protected accounts to verify:

   ```bash
   python scripts/admin/rfu_admin.py list-protected-accounts \
      --database-path <db>
   ```

3. **Login** with break-glass account and provide justification

4. **Unblock** the original admin:

   ```bash
   python scripts/admin/rfu_admin.py unblock-user \
      --database-path <db> \
      --username <original_admin> \
      --justification "Recovery from lockout"
   ```

5. **Rotate** break-glass credentials:
   ```bash
   python scripts/admin/rfu_admin.py rotate-break-glass \
      --database-path <db> \
      --username rfu_dev_breakglass
   ```

### Headless Recovery (No GUI)

All recovery operations work without GUI authentication:

- Bootstrap, list, rotate, and unblock commands operate directly on database
- No QApplication or PyQt5 required
- Credentials exported to secure files for out-of-band transfer
- Full audit trail maintained for compliance

---

## Admin Panel Features (Dev Only)

The admin panel includes dev-only features for monitoring break-glass usage:

### Break-Glass History

```python
from src.rfu.admin_panel import AdminPanelActions

actions = AdminPanelActions(database_path, current_user_role='dev')
history = actions.break_glass_history()
# Returns list of usage log entries with timestamps, justifications
```

### Always-Available Status

```python
status = actions.always_available_status()
# Returns cooldown status and last usage for always-available accounts
```

### Protected Accounts Summary

```python
summary = actions.protected_accounts_summary()
# Returns combined status of all protected accounts
```

**Access Control**: These methods require `dev` role. Access from lower roles
raises `PermissionError`.

---

## Secure Secret Dispatcher (T080)

### Console / CLI delivery

- Temporary secret is rendered once in the CLI payload and immediately cleared
  from the database; the reset request transitions to `delivered`.
- Operators **must** pass `--confirm-display` to `rfu-admin reset-password`
  whenever the delivery channel is `console` or `cli`.

### Secure note delivery

- Secrets are encrypted with `cryptography.Fernet` and stored in
  `<database dir>/secure_resets/rfu_reset_secret_<user>_<timestamp>.secure-note`.
- The CLI prints both the note path and one-time key so administrators can move
  secrets out-of-band without exposing them in the console.

Additional guarantees:

- Every reset request persists justification text, dispatcher channel, and
  status (`pending → delivered`).
- Dispatcher emits a dedicated audit entry (`dispatcher_event=true`) so
  compliance tooling can distinguish interactive admin actions from the
  delivery step.
- Attempting to dispatch the same `reset_request_id` twice raises
  `SecretAlreadyDeliveredError`/`SecretUnavailableError` and nothing is printed
  again.

## CLI Checklist

### Reset Password

```bash
python scripts/admin/rfu_admin.py reset-password \
   --database-path <db> \
   --username <user> \
   --delivery console|secure_note|cli \
   --justification "<why>" \
   [--confirm-display]  # required for console/cli deliveries
```

- Returns a payload containing `reset_request_id`, `secret_revealed`, and either
  `temporary_password` (console/cli) or `secret_note_path` + `secret_note_key`
  (secure note).
- Automatically seeds the `rfu-admin` bootstrap account if no actor is
  provided.

### Approvals & Unblock

`approve-user` and `unblock-user` reuse the same justification pipeline and log
entries; no functional changes beyond the shared audit metadata.

### Audit Export & Idle Watchdog

`audit-export` now defaults to a 30-day window (limit 1000) and writes
JSON bundles that highlight dispatcher metadata. `idle-watchdog` continues to
exit with code `2` whenever sessions are revoked for automation friendliness.

### MFA Readiness Hooks

Placeholders exist for `mfa-status` and `mfa-enroll`. Both commands execute
controller plumbing and immediately raise `MFAFeatureUnavailableError` while we
finalize the MFA UX. Their presence ensures scripts and docs already reference
future MFA entry points.

## Contract & Integration Coverage (T081)

The new contract test `tests/contracts/identity/test_secure_reset_workflow.py`
verifies:

1. Reset calls reject empty justification text.
2. Console delivery is blocked without `--confirm-display`.
3. Dispatcher delivers secrets once and records audit metadata.

Complementary integration tests keep enforcing CLI role checks and logging.
Use these tests when validating regressions in future releases.
