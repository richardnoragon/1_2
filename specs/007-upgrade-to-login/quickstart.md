# Quickstart: Login & Password Integration Upgrade — Lockout Prevention

**Feature**: 007-upgrade-to-login  
**Date**: 2025-11-26  
**Validates**: FR-001 through FR-018 from spec.md

---

## Prerequisites

1. Python 3.8+ with virtual environment activated
2. Database at `data/identity/rfu_identity.sqlite3`
3. Dependencies installed: `pip install -r requirements.txt`

---

## Quick Validation Steps

### 1. Verify Protected Accounts Exist

```bash
# List always-available and break-glass accounts
python -m scripts.admin.rfu_admin list-protected-accounts \
    --database-path data/identity/rfu_identity.sqlite3
```

**Expected Output**:

```
Protected Accounts:
┌─────────────────────────┬───────┬──────────────────┬────────────┐
│ Username                │ Role  │ Type             │ Status     │
├─────────────────────────┼───────┼──────────────────┼────────────┤
│ rfu_dev_always          │ dev   │ always-available │ active     │
│ rfu_admin_always        │ admin │ always-available │ active     │
│ rfu_dev_breakglass      │ dev   │ break-glass      │ disabled   │
│ rfu_admin_breakglass    │ admin │ break-glass      │ disabled   │
└─────────────────────────┴───────┴──────────────────┴────────────┘
```

### 2. Test Always-Available Account Protection

```bash
# Attempt to delete always-available account (should fail)
python -m scripts.admin.rfu_admin delete-user \
    --database-path data/identity/rfu_identity.sqlite3 \
    --username rfu_admin_always
```

**Expected Output**:

```
[ERROR] Cannot delete always-available account: rfu_admin_always
Action blocked and logged to AdminActionAudit.
```

### 3. Test Auto-Unblock Mechanism

```bash
# Simulate 5 failed logins to trigger block
for i in {1..5}; do
    python -m scripts.admin.rfu_admin test-login \
        --database-path data/identity/rfu_identity.sqlite3 \
        --username rfu_admin_always \
        --password wrong_password
done

# Check account status
python -m scripts.admin.rfu_admin get-user \
    --database-path data/identity/rfu_identity.sqlite3 \
    --username rfu_admin_always
```

**Expected Output**:

```
Account Status:
  username: rfu_admin_always
  is_blocked: true
  auto_unblock_at: 2025-11-26T10:35:00Z (5 minutes from now)
```

```bash
# Wait 5 minutes, then check again
python -m scripts.admin.rfu_admin check-auto-unblock \
    --database-path data/identity/rfu_identity.sqlite3 \
    --username rfu_admin_always
```

**Expected Output**:

```
[OK] Account rfu_admin_always auto-unblocked after cooldown.
```

### 4. Test Break-Glass Login Flow

```bash
# Enable break-glass access
export RFU_ENABLE_BREAK_GLASS=true

# Login with break-glass credentials (requires justification)
python -m scripts.admin.rfu_admin break-glass-login \
    --database-path data/identity/rfu_identity.sqlite3 \
    --username rfu_admin_breakglass \
    --password <from_secure_storage> \
    --justification "Emergency: primary admin locked out and cooldown not expired"
```

**Expected Output**:

```
[WARN] Break-glass session started. All actions will be logged.
Session ID: bg_sess_abc123
Usage logged to BreakGlassUsageLog.

Perform recovery actions, then logout:
  python -m scripts.admin.rfu_admin break-glass-logout --session-id bg_sess_abc123
```

```bash
# End break-glass session
python -m scripts.admin.rfu_admin break-glass-logout \
    --session-id bg_sess_abc123
```

**Expected Output**:

```
[OK] Break-glass session ended.
Password rotation triggered.
New credentials exported to: config/break_glass_credentials_20251126.secure
⚠️  Please update offline credential storage and acknowledge rotation.
```

### 5. Verify Role Enforcement

```bash
# Test readonly role cannot perform write operations
python -m scripts.admin.rfu_admin test-permission \
    --database-path data/identity/rfu_identity.sqlite3 \
    --username readonly_user \
    --action modify_data
```

**Expected Output**:

```
Permission Check:
  role: readonly
  action: modify_data
  allowed: false
  reason: Write access denied for readonly role
```

```bash
# Test dev role has all capabilities
python -m scripts.admin.rfu_admin test-permission \
    --database-path data/identity/rfu_identity.sqlite3 \
    --username rfu_dev_always \
    --action access_debugging
```

**Expected Output**:

```
Permission Check:
  role: dev
  action: access_debugging
  allowed: true
```

### 6. Verify Lockout Prevention Health

```bash
python -m scripts.admin.rfu_admin health-check \
    --database-path data/identity/rfu_identity.sqlite3 \
    --lockout-prevention
```

**Expected Output**:

```
Lockout Prevention Health Check:
  healthy: true
  always_available_accounts:
    - rfu_dev_always: accessible
    - rfu_admin_always: accessible
  break_glass_accounts:
    - rfu_dev_breakglass: disabled (ready for emergency)
    - rfu_admin_breakglass: disabled (ready for emergency)
  accessible_paths:
    - always_available_dev
    - always_available_admin
    - break_glass_dev (when enabled)
    - break_glass_admin (when enabled)
    - cli_rescue_script
```

---

## GUI Validation (when available)

1. **Login Dialog**: Launch hub, verify login dialog appears before main window
2. **Admin Panel**: Login as admin, verify protected accounts show lock icon
3. **Break-Glass Prompt**: Enable break-glass, verify justification dialog appears
4. **Readonly Mode**: Login as readonly, verify write operations are disabled

---

## Database Verification Queries

```sql
-- Verify protected accounts exist
SELECT username, role, is_always_available, is_break_glass, account_status
FROM user_accounts
WHERE is_always_available = 1 OR is_break_glass = 1;

-- Verify role distribution
SELECT role, COUNT(*) as count
FROM user_accounts
GROUP BY role;

-- Check for pending rotations
SELECT account_username, login_timestamp, post_usage_rotation_status
FROM break_glass_usage_log
WHERE post_usage_rotation_status = 'pending';

-- Verify audit trail
SELECT action_type, COUNT(*) as count
FROM admin_action_audit
WHERE created_at > datetime('now', '-7 days')
GROUP BY action_type;
```

---

## Success Criteria

| Requirement                        | Validation                    | Status |
| ---------------------------------- | ----------------------------- | ------ |
| FR-001 (Four roles)                | Role matrix enforced          | ☐      |
| FR-002 (Role hierarchy)            | Dev > Admin > User > Readonly | ☐      |
| FR-004 (Always-available accounts) | 2 accounts exist              | ☐      |
| FR-005 (Deletion protection)       | Delete blocked                | ☐      |
| FR-006 (Auto-unblock)              | 5-min cooldown works          | ☐      |
| FR-009 (Break-glass accounts)      | 2 accounts exist              | ☐      |
| FR-011 (Enhanced audit)            | Usage logged                  | ☐      |
| FR-012 (Password rotation)         | Triggered on logout           | ☐      |
| FR-016 (Never locked out)          | Health check passes           | ☐      |
| FR-017 (CLI recovery)              | Headless path works           | ☐      |

---

## Troubleshooting

### "Account not found"

Ensure bootstrap has run:

```bash
python -m scripts.admin.rfu_admin bootstrap-protected-accounts \
    --database-path data/identity/rfu_identity.sqlite3
```

### "Break-glass access not enabled"

Set environment variable or CLI flag:

```bash
export RFU_ENABLE_BREAK_GLASS=true
# or
python -m scripts.admin.rfu_admin ... --enable-break-glass
```

### "Invariant violation detected"

Run rescue script to restore protected accounts:

```bash
python rescue.py bootstrap data/identity/rfu_identity.sqlite3
```

---

**Quickstart Complete**: Run all validation steps before marking feature complete.
