# Quickstart — Verifying Login & Password Baseline Integration

> Motto reminder: **ship many focused steps**. Each verification below is a tiny, isolated check you can run independently.

## Prerequisites

- Python 3.12 virtual environment activated (`.venv312`).
- SQLite database migrated to latest schema (`python scripts/db/manage.py migrate`).
- CLI helper `rfu-admin` on PATH (invokes `python rfu_explorer.py --admin`).

## 1. Bootstrap Admin + Pending User

```bash
# Seed default admin + demo user
python scripts/admin/bootstrap_identity.py --username admin --password "TempAdm1n!"
python scripts/admin/create_pending_user.py --username demo --email demo@example.com
```

- Expected: `demo` appears in `user_accounts` with `account_status=pending`.

## 2. Approve Pending User (CLI)

Set `DB_PATH` to the SQLite file created during bootstrapping (e.g., `data/rfu_identity.sqlite3`).

```bash
python scripts/admin/rfu_admin.py approve-user \
   --database-path "$DB_PATH" \
   --username demo \
   --role standard \
   --preferences-template default
```

- Expected: CLI prints activation success, `preferences_id` assigned, audit entry logged with `origin_surface="cli"`.

## 3. Login via Hub UI

1. Launch hub: `python src/rfu/main.py`.
2. Enter `demo` / generated password.
3. Confirm personalized workspace loads (look for preferences badge).

## 4. Lockout Guard

```bash
python scripts/admin/simulate_failed_logins.py --username demo --attempts 5
```

- Expected: `account_status` flips to `blocked`, audit log contains `login_failure` burst, CLI `rfu-admin unblock-user demo --reason "QA"` resets state.

## 5. Password Reset Terminates Sessions (Dispatcher Enabled)

1. Login as `demo` (GUI) and leave app idle.
2. In a separate terminal run:

   ```bash
   python scripts/admin/rfu_admin.py reset-password \
      --database-path "$DB_PATH" \
      --username demo \
      --delivery console \
      --justification "QA forced reset" \
      --confirm-display
   ```

3. Hub should immediately force logout. The CLI payload now returns
   `reset_request_id`, `secret_revealed=true`, and a single-use
   `temporary_password`. Omitting `--confirm-display` intentionally fails the
   command so secrets are never shown without administrator approval.

**Secure note variant**

```bash
python scripts/admin/rfu_admin.py reset-password \
   --database-path "$DB_PATH" \
   --username demo \
   --delivery secure_note \
   --justification "QA secure note"
```

- Output includes `secret_note_path` plus `secret_note_key`. The encrypted
  `.secure-note` file lands in `<database dir>/secure_resets/` and can be handed
  off without exposing the password in the console.

## 6. Idle Timeout

- Leave a fresh session idle for >10 minutes. Verify hub returns to login screen and CLI commands prompt for credentials again.

## 7. Preference Sharing Guard

```bash
python scripts/admin/rfu_admin.py export-preferences \
   --database-path "$DB_PATH" \
   --username demo \
   --purpose "team sync"
```

- Expected: Command fails unless `share_preferences` flag enabled; once enabled, exported JSON omits identity data and contains metadata envelope.

## 8. MFA Placeholder Wiring

```bash
python scripts/admin/rfu_admin.py mfa-status --database-path "$DB_PATH"
python scripts/admin/rfu_admin.py mfa-enroll \
    --database-path "$DB_PATH" \
    --username demo \
    --actor-username admin
```

- Both commands currently exit with `MFAFeatureUnavailableError` (exit code 3)
  but exercise the controller plumbing so future MFA work only needs to replace
  the placeholder responses.

Document outcomes in the upcoming `/tasks` checklist to ensure each verification becomes a discrete, automatable test.

## 9. Bootstrap Protected Accounts (Lockout Prevention)

```bash
python scripts/admin/rfu_admin.py bootstrap-protected-accounts \
   --database-path "$DB_PATH" \
   --export-credentials secure_note
```

- Expected: Creates two always-available accounts (one `dev`, one `admin`) and two break-glass accounts (one `dev`, one `admin`). Credentials exported to encrypted secure-note files in `<database dir>/protected_credentials/`.

## 10. Always-Available Account Cooldown

```bash
# Simulate 5 failed logins for always-available admin
python scripts/admin/simulate_failed_logins.py --username always_available_admin --attempts 5
```

- Expected: `account_status` flips to `blocked`, but `auto_unblock_at` is set to current time + 15 minutes. After cooldown expires, account automatically unblocks.

## 11. Break-Glass Emergency Access

```bash
# Login with break-glass credentials (requires justification)
python scripts/admin/rfu_admin.py break-glass-login \
   --database-path "$DB_PATH" \
   --username break_glass_admin \
   --justification "Primary admin account compromised during incident #12345"
```

- Expected: Session marked as break-glass, enhanced audit logging enabled, all administrators notified. Upon logout, credential rotation is triggered automatically.

## 12. List Protected Accounts

```bash
python scripts/admin/rfu_admin.py list-protected-accounts \
   --database-path "$DB_PATH"
```

- Expected: Shows status of always-available and break-glass accounts including last login, cooldown status, and rotation status.

## 13. Rotate Break-Glass Credentials

```bash
python scripts/admin/rfu_admin.py rotate-break-glass \
   --database-path "$DB_PATH" \
   --account break_glass_dev \
   --export-credentials secure_note \
   --justification "Post-incident credential rotation"
```

- Expected: New credentials generated, old credentials invalidated, audit entry logged, secure-note file created for offline storage.

## 14. Verify Lockout Prevention Guarantee

```bash
python scripts/admin/verify_lockout_prevention.py --database-path "$DB_PATH"
```

- Expected: Script confirms at least one administrative access path is always available (always-available accounts not all blocked, or break-glass accounts accessible).
