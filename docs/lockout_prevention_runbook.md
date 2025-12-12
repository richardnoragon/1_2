# Lockout Prevention Runbook

This runbook provides step-by-step procedures for recovering from lockout
scenarios and managing protected accounts in RFU.

---

## Table of Contents

1. [Overview](#overview)
2. [Protected Account Types](#protected-account-types)
3. [CLI Command Reference](#cli-command-reference)
4. [Recovery Procedures](#recovery-procedures)
5. [Health Check Interpretation](#health-check-interpretation)
6. [Break-Glass Credential Rotation](#break-glass-credential-rotation)
7. [Troubleshooting](#troubleshooting)

---

## Overview

The lockout prevention system ensures administrators can never be completely
locked out of the RFU system. It provides:

- **Always-Available Accounts**: Never blocked by failed login attempts
- **Break-Glass Accounts**: Emergency access with justification tracking
- **Automatic Cooldown**: Temporary blocks auto-expire after 5 minutes
- **CLI Recovery**: All operations work without GUI authentication

### Key Invariant

> At least one administrative access path is always available, either through
> an always-available account or a break-glass account.

---

## Protected Account Types

### Always-Available Accounts

| Account            | Role  | Purpose                       |
| ------------------ | ----- | ----------------------------- |
| `rfu_dev_always`   | dev   | Developer access, never locks |
| `rfu_admin_always` | admin | Admin access, never locks     |

**Characteristics:**

- `is_always_available = True`
- Cannot be blocked by failed login attempts
- Login attempts are tracked but lockout threshold ignored
- Use for routine administration

### Break-Glass Accounts

| Account                | Role  | Purpose                    |
| ---------------------- | ----- | -------------------------- |
| `rfu_dev_breakglass`   | dev   | Emergency developer access |
| `rfu_admin_breakglass` | admin | Emergency admin access     |

**Characteristics:**

- `is_break_glass = True`
- Require justification at login (minimum 10 characters)
- All usage logged to `break_glass_usage_log` table
- Credentials must be rotated after each use
- Reserved for true emergency scenarios

---

## CLI Command Reference

All commands use the RFU admin CLI at `scripts/admin/rfu_admin.py`.

### Bootstrap Protected Accounts

Initialize protected accounts on a fresh or recovered database:

```bash
python scripts/admin/rfu_admin.py bootstrap-protected-accounts \
    --database-path data/identity/rfu_identity.sqlite3 \
    --show-console \
    --export-credentials
```

**Options:**

| Flag                   | Description                  | Default  |
| ---------------------- | ---------------------------- | -------- |
| `--database-path`      | Path to identity database    | Required |
| `--show-console`       | Display passwords on console | True     |
| `--no-show-console`    | Suppress password display    | -        |
| `--export-credentials` | Export to secure file        | True     |

**Output:**

- Creates all 4 protected accounts if not present
- Exports credentials to `config/protected_credentials_<timestamp>.secure`
- Displays temporary passwords on console (if enabled)

### List Protected Accounts

View status of all protected accounts:

```bash
python scripts/admin/rfu_admin.py list-protected-accounts \
    --database-path data/identity/rfu_identity.sqlite3
```

**Output Format (JSON):**

```json
{
  "complete": true,
  "accounts": [
    {
      "username": "rfu_dev_always",
      "role": "dev",
      "type": "always_available",
      "status": "active",
      "is_blocked": false
    }
  ],
  "missing": []
}
```

### Check Lockout Prevention Health

Verify the lockout prevention invariant:

```bash
python scripts/admin/rfu_admin.py check-lockout-health \
    --database-path data/identity/rfu_identity.sqlite3
```

**Output Format (JSON):**

```json
{
  "healthy": true,
  "accessible_paths": [
    {
      "account_username": "rfu_dev_always",
      "role": "dev",
      "account_type": "always_available",
      "is_accessible": true
    }
  ],
  "blocked_count": 0,
  "has_dev_access": true,
  "has_admin_access": true
}
```

### Unblock User Account

Manually unblock any user account:

```bash
python scripts/admin/rfu_admin.py unblock-user \
    --database-path data/identity/rfu_identity.sqlite3 \
    --username <username> \
    --justification "Reason for unblocking"
```

**Notes:**

- Works for any account, including protected accounts
- Creates audit log entry
- Resets `login_attempts` to 0

### Rotate Break-Glass Credentials

Rotate credentials after break-glass usage:

```bash
python scripts/admin/rfu_admin.py rotate-break-glass \
    --database-path data/identity/rfu_identity.sqlite3 \
    --username rfu_dev_breakglass \
    --show-console \
    --export-credentials
```

**Options:**

| Flag                   | Description                     | Default  |
| ---------------------- | ------------------------------- | -------- |
| `--username`           | Break-glass account to rotate   | Required |
| `--show-console`       | Display new password on console | True     |
| `--export-credentials` | Export to secure file           | True     |

---

## Recovery Procedures

### Scenario 1: All Normal Accounts Locked Out

**Symptoms:**

- Cannot log in with any admin account
- System shows "account blocked" for all attempts

**Recovery Steps:**

1. **Verify protected accounts exist:**

   ```bash
   python scripts/admin/rfu_admin.py list-protected-accounts \
       --database-path data/identity/rfu_identity.sqlite3
   ```

2. **If protected accounts exist, log in with always-available:**

   Use `rfu_dev_always` or `rfu_admin_always` credentials.

3. **If protected accounts don't exist, bootstrap:**

   ```bash
   python scripts/admin/rfu_admin.py bootstrap-protected-accounts \
       --database-path data/identity/rfu_identity.sqlite3 \
       --show-console --export-credentials
   ```

4. **Unblock your regular admin account:**

   ```bash
   python scripts/admin/rfu_admin.py unblock-user \
       --database-path data/identity/rfu_identity.sqlite3 \
       --username your_admin_account \
       --justification "Recovery from lockout"
   ```

### Scenario 2: Protected Account Credentials Lost

**Symptoms:**

- Protected accounts exist but passwords unknown
- Original credential files deleted or inaccessible

**Recovery Steps:**

1. **For break-glass accounts, rotate credentials:**

   ```bash
   python scripts/admin/rfu_admin.py rotate-break-glass \
       --database-path data/identity/rfu_identity.sqlite3 \
       --username rfu_dev_breakglass \
       --show-console
   ```

2. **For always-available accounts:**

   Always-available accounts cannot be directly rotated via CLI.
   Options:

   - Use break-glass account to reset the password
   - Direct database access (last resort, see Scenario 4)

### Scenario 3: Break-Glass Login Required

**Symptoms:**

- Normal admin access unavailable
- Need emergency access with audit trail

**Recovery Steps:**

1. **Prepare justification:**

   Write a clear explanation (minimum 10 characters) describing:

   - Why emergency access is needed
   - What actions will be performed
   - Incident ticket number (if applicable)

2. **Log in via break-glass:**

   - Use `rfu_dev_breakglass` or `rfu_admin_breakglass`
   - Enter prepared justification when prompted

3. **Perform necessary recovery actions:**

   All actions are logged to `break_glass_usage_log`.

4. **Log out when complete.**

5. **Rotate break-glass credentials immediately:**

   ```bash
   python scripts/admin/rfu_admin.py rotate-break-glass \
       --database-path data/identity/rfu_identity.sqlite3 \
       --username rfu_dev_breakglass \
       --show-console --export-credentials
   ```

6. **Securely store new credentials.**

### Scenario 4: Complete Database Recovery

**Symptoms:**

- Database corrupted or lost
- Starting from scratch with new database

**Recovery Steps:**

1. **Create new database:**

   ```bash
   python scripts/admin/rfu_admin.py init-database \
       --database-path data/identity/rfu_identity.sqlite3
   ```

2. **Run migrations:**

   ```bash
   python scripts/admin/rfu_admin.py run-migrations \
       --database-path data/identity/rfu_identity.sqlite3
   ```

3. **Bootstrap protected accounts:**

   ```bash
   python scripts/admin/rfu_admin.py bootstrap-protected-accounts \
       --database-path data/identity/rfu_identity.sqlite3 \
       --show-console --export-credentials
   ```

4. **Securely store all credentials:**

   - Move `config/protected_credentials_*.secure` to secure storage
   - Update password manager or vault
   - Verify file permissions are restrictive (600 on Unix)

---

## Health Check Interpretation

### Health Status Fields

| Field              | Description                                |
| ------------------ | ------------------------------------------ |
| `healthy`          | True if at least one path is accessible    |
| `accessible_paths` | List of all protected accounts with status |
| `blocked_count`    | Number of accounts in cooldown             |
| `has_dev_access`   | True if dev-level access is available      |
| `has_admin_access` | True if admin-level access is available    |
| `reason`           | Human-readable status message              |

### Interpreting Results

**Healthy Status (`healthy: true`):**

- At least one protected account is accessible
- System can be administered normally
- `blocked_count > 0` indicates accounts in cooldown (will auto-unblock)

**Unhealthy Status (`healthy: false`):**

- No accessible paths available
- All protected accounts may be blocked
- Break-glass accounts may need credentials
- Immediate action required

### Common Health Check Messages

| Message                         | Meaning                                    |
| ------------------------------- | ------------------------------------------ |
| `no accessible paths available` | All protected accounts blocked/unavailable |
| `N account(s) in cooldown`      | N accounts will auto-unblock soon          |
| (empty reason)                  | System is fully healthy                    |

---

## Break-Glass Credential Rotation

### When to Rotate

- **Immediately** after any break-glass login
- After suspected credential compromise
- Per security policy schedule (e.g., quarterly)

### Rotation Process

1. **Verify current session is ended:**

   Ensure break-glass user is logged out.

2. **Execute rotation command:**

   ```bash
   python scripts/admin/rfu_admin.py rotate-break-glass \
       --database-path data/identity/rfu_identity.sqlite3 \
       --username rfu_dev_breakglass \
       --export-credentials
   ```

3. **Secure new credentials:**

   - Move exported file to secure storage
   - Update password vault/manager
   - Delete local credential file

4. **Verify rotation:**

   ```bash
   python scripts/admin/rfu_admin.py list-protected-accounts \
       --database-path data/identity/rfu_identity.sqlite3
   ```

   Check `updated_at` timestamp for the rotated account.

### Credential File Format

```text
# RFU Protected Account Credentials
# Generated: 20240115_103045
# SECURE THIS FILE IMMEDIATELY
#
# Format: username | role | type | password

rfu_dev_breakglass | dev | break_glass | <random-24-char-password>

# After securing, delete this file
```

---

## Troubleshooting

### Problem: "break-glass access not enabled"

**Cause:** Attempting break-glass login without proper enablement.

**Solution:**

- Ensure `RFU_ENABLE_BREAK_GLASS=1` environment variable is set
- Or use the appropriate CLI flag to enable break-glass mode

### Problem: "justification required"

**Cause:** Break-glass login attempted without justification.

**Solution:**

- Provide justification of at least 10 characters
- Include incident reference if applicable

### Problem: "account not found"

**Cause:** Protected accounts not bootstrapped.

**Solution:**

```bash
python scripts/admin/rfu_admin.py bootstrap-protected-accounts \
    --database-path data/identity/rfu_identity.sqlite3
```

### Problem: "cooldown not expired"

**Cause:** Attempting to unblock account before cooldown period ends.

**Solution:**

- Wait for cooldown to expire (default 5 minutes)
- Check `auto_unblock_at` timestamp
- Or use always-available account to access system

### Problem: Health check shows `healthy: false`

**Cause:** All protected accounts inaccessible.

**Solution:**

1. Check if accounts exist:

   ```bash
   python scripts/admin/rfu_admin.py list-protected-accounts
   ```

2. Bootstrap if missing:

   ```bash
   python scripts/admin/rfu_admin.py bootstrap-protected-accounts
   ```

3. Rotate credentials if needed:
   ```bash
   python scripts/admin/rfu_admin.py rotate-break-glass --username <account>
   ```

---

## Appendix: Quick Reference Card

### Emergency Access

```bash
# 1. Check health
python scripts/admin/rfu_admin.py check-lockout-health --database-path <db>

# 2. If unhealthy, bootstrap
python scripts/admin/rfu_admin.py bootstrap-protected-accounts --database-path <db>

# 3. Unblock account
python scripts/admin/rfu_admin.py unblock-user --database-path <db> --username <user> --justification "<reason>"

# 4. After break-glass use, rotate
python scripts/admin/rfu_admin.py rotate-break-glass --database-path <db> --username <account>
```

### Protected Account Quick Status

```bash
python scripts/admin/rfu_admin.py list-protected-accounts --database-path <db> | python -c "import sys,json; d=json.load(sys.stdin); print('Complete' if d['complete'] else 'Missing: '+', '.join(d['missing']))"
```

---

> Based on Constitution v1.3.0 — See `.specify/memory/constitution.md`
> Part of 007-upgrade-to-login lockout prevention feature
