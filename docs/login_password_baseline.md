# Login & Password Baseline – Secure Reset + CLI Notes

The Phase 3.7 polish pass adds a hardened reset workflow around
`SecureSecretDispatcher`, refreshed CLI helpers, and documentation for MFA
readiness. This page captures the operational expectations for QA, support, and
future development.

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
