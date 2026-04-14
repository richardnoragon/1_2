# TOTP Specification — Offline-Capable MFA
<!-- Version: 1.0 | Constitution: v1.22.0 | Q9 Applied -->

## 1. Purpose

This document is the canonical specification for Time-Based One-Time Password
(TOTP) MFA in RFU. It prescribes the mandatory interoperability profile,
enrollment and verification requirements, backup code rules, export/import
behaviour, and CI enforcement criteria.

**Constitutional authority**: §VII.X (§VII.X.1–§VII.X.7) and §G.9.

---

## 2. Governing Standards

| Item | Value |
|------|-------|
| Primary standard | RFC 6238 (TOTP — Time-Based One-Time Password Algorithm) |
| Underlying standard | RFC 4226 (HOTP — HMAC-Based One-Time Password Algorithm) |
| HOTP status | MAY be supported for legacy fallback; MUST NOT be enrolled as primary MFA method |

---

## 3. Default TOTP Profile (Constitutional Minimum)

All implementations MUST support the following profile. This is §G.9 of the
constitution.

| Parameter | Constitutional value | Rationale |
|-----------|---------------------|-----------|
| Algorithm | HMAC-SHA1 | Universal authenticator support |
| Code digits | 6 | Universal default |
| Time step | 30 seconds | Universal default |
| Drift tolerance | ±1 time step (±30 s) | Compensates for typical clock skew |

### 3.1 Normative Provisioning URI

```
otpauth://totp/Label?secret=SECRET&issuer=APP&algorithm=SHA1&digits=6&period=30
```

- `Label` MUST identify the account (e.g., `user@rfuapp`).
- `SECRET` MUST be the Base32-encoded TOTP secret (no padding required in the
  URI; implementations MUST accept both padded and unpadded).
- `issuer` SHOULD identify the application.

### 3.2 Optional Additional Profiles

Implementations MAY register additional profiles (e.g., SHA-256, SHA-512,
8-digit codes, 60-second steps) as secondary configured options. These MUST
NOT replace or disable the default profile. An implementation that supports
only a non-default profile is non-conformant.

---

## 4. Enrollment Requirements (§VII.X.3)

1. Generate a cryptographically random TOTP secret of at least 160 bits
   (20 bytes) from a CSPRNG.
2. Construct a provisioning URI using the default profile (§3.1).
3. Display the provisioning URI as a QR code and/or manual entry form to the
   user.
4. Ask the user to confirm enrollment by entering one valid TOTP code before
   persisting the secret.
5. Store the TOTP secret encrypted at rest using the application's symmetric
   storage key (same tier as password hash storage).
6. Emit an audit entry: `mfa_enrollment`, including account ID and timestamp.

---

## 5. Verification Requirements (§VII.X.4)

### 5.1 Drift Window

Given the server's current UNIX timestamp `T` and time step `S = 30`:

```
counter_current = T // S
accepted_counters = [counter_current - 1, counter_current, counter_current + 1]
```

All three counters MUST be checked. The user's code is accepted if it matches
any of the three expected TOTP values.

Counters outside the ±1 window MUST be rejected.

### 5.2 Replay Prevention

Once a code is accepted, the (counter, code) pair MUST be invalidated so that
the same code cannot be used for a second authentication within the same
window.

### 5.3 Unsupported Configs

If a user-provided code is generated with a non-default profile (e.g.,
SHA-256), it MUST be rejected unless the implementation has explicitly
configured that profile as an optional secondary profile and the account was
enrolled with that profile.

---

## 6. Backup and Recovery Codes (§VII.X.5)

- Single-use backup codes MAY be generated at enrollment time and shown to the
  user exactly once.
- Each code MUST be generated from a CSPRNG with at least 128 bits of entropy.
- Codes MUST be stored as one-way hashes (e.g., bcrypt or Argon2id), not in
  plaintext.
- Backup codes MUST NOT count as an enrolled MFA method for activation-gate
  purposes (§VII.X.5).
- Using a backup code MUST emit an audit entry: `mfa_backup_code_used`,
  including account ID and timestamp.
- An administrator MUST be notified when a backup code is used.

---

## 7. Export and Import of MFA Configuration (§VII.X.6)

- Export payloads MUST include the TOTP secret and the profile parameters
  (algorithm, digits, period).
- The TOTP secret MUST be encrypted in the export envelope per §VI.4
  (AES-256-GCM + Argon2id).
- Importers MUST NOT alter the TOTP secret or profile parameters unless
  explicitly migrating from a documented legacy format.
- After import, the implementation MUST accept codes generated using the
  default profile (§G.9).

### 7.1 Export Record Shape

```json
{
  "mfa_type": "totp",
  "profile": {
    "algorithm": "SHA1",
    "digits": 6,
    "period": 30
  },
  "secret_encrypted": "<base64-encoded AES-256-GCM ciphertext per §VI.4>",
  "enrolled_at": "<ISO-8601 timestamp>",
  "account_id": "<UUID>"
}
```

---

## 8. Reference Implementation

```python
"""
totp_reference.py — Constitutional default TOTP profile
Standard: RFC 6238  |  Constitution: §VII.X, §G.9  |  Spec: docs/totp-spec.md
"""

import hmac, hashlib, struct, time, base64
from typing import List

TOTP_ALGORITHM = "sha1"
TOTP_DIGITS = 6
TOTP_PERIOD = 30
TOTP_DRIFT = 1  # ±1 time step


def _hotp(secret_bytes: bytes, counter: int) -> int:
    """Compute HOTP value per RFC 4226."""
    msg = struct.pack(">Q", counter)
    h = hmac.new(secret_bytes, msg, hashlib.sha1).digest()
    offset = h[-1] & 0x0F
    code = struct.unpack(">I", h[offset : offset + 4])[0] & 0x7FFFFFFF
    return code % (10 ** TOTP_DIGITS)


def generate_totp(secret_b32: str, at_time: float | None = None) -> str:
    """Generate a 6-digit TOTP code for the given Base32 secret."""
    secret_bytes = base64.b32decode(secret_b32.upper().strip("=") + "=" * (-len(secret_b32) % 8))
    t = int((at_time or time.time()) // TOTP_PERIOD)
    code = _hotp(secret_bytes, t)
    return str(code).zfill(TOTP_DIGITS)


def _accepted_counters(at_time: float | None = None) -> List[int]:
    t = int((at_time or time.time()) // TOTP_PERIOD)
    return [t - TOTP_DRIFT + i for i in range(TOTP_DRIFT * 2 + 1)]


def verify_totp(
    secret_b32: str,
    user_code: str,
    at_time: float | None = None,
    used_counters: set | None = None,
) -> bool:
    """
    Verify a TOTP code.  Returns True if accepted.
    Pass `used_counters` (a mutable set) for replay prevention.
    """
    secret_bytes = base64.b32decode(secret_b32.upper().strip("=") + "=" * (-len(secret_b32) % 8))
    for counter in _accepted_counters(at_time):
        expected = str(_hotp(secret_bytes, counter)).zfill(TOTP_DIGITS)
        if hmac.compare_digest(expected, user_code.strip()):
            if used_counters is not None:
                if counter in used_counters:
                    return False  # Replay
                used_counters.add(counter)
            return True
    return False


def make_provisioning_uri(secret_b32: str, label: str, issuer: str) -> str:
    """Build otpauth:// URI using the constitutional default profile."""
    clean_secret = secret_b32.upper().replace(" ", "")
    return (
        f"otpauth://totp/{label}"
        f"?secret={clean_secret}&issuer={issuer}"
        f"&algorithm=SHA1&digits=6&period=30"
    )
```

---

## 9. CI Test Specification (§VII.X.7)

### 9.1 Unit Tests

| ID | Name | Pass condition |
|----|------|----------------|
| T1 | Default profile interoperability | Code generated with reference impl matches code from a known-good library at the same timestamp |
| T2 | Drift tolerance — current window | Code generated at `T` accepted when server is at `T` |
| T3 | Drift tolerance — lag window | Code generated at `T - 30s` accepted when server is at `T` |
| T4 | Drift tolerance — lead window | Code generated at `T + 30s` accepted when server is at `T` |
| T5 | Drift rejection — too early | Code generated at `T - 60s` REJECTED when server is at `T` |
| T6 | Drift rejection — too late | Code generated at `T + 60s` REJECTED when server is at `T` |
| T7 | Replay prevention | Accepted code for counter `C` rejected on second use with same `C` |
| T8 | Backup code exclusion | Backup code does not satisfy MFA enrollment check |
| T9 | HOTP exclusion | HOTP-enrolled account fails activation-gate check |
| T10 | Wrong digit length rejected | 8-digit code rejected when account enrolled with 6-digit default |

### 9.2 Static Analysis

CI MUST detect:
- `algorithm=SHA1` (or equivalent) in TOTP enrollment paths
- `digits=6`, `period=30` in provisioning URI construction
- No path where HOTP is used as the sole enrolled method for activation gate
- No path where backup codes satisfy `has_enrolled_mfa()` logic

### 9.3 CI Failure Conditions

CI MUST fail if any of the following are true:
- TOTP default profile (SHA-1 / 6 / 30 s) is not supported
- Drift tolerance is absent, zero, or > ±1 step
- HOTP can be treated as an enrolled MFA method
- Backup codes can be treated as an enrolled MFA method
- Any T1–T10 test is absent or failing
- Provisioning URI encodes a non-default algorithm, digit length, or period
  without an explicit secondary-profile configuration guard

---

## 10. Migration Plan for Existing MFA Implementations

| Step | Action |
|------|--------|
| 1 | Inventory: identify all TOTP, HOTP, and backup code checks in the codebase |
| 2 | Standardise enrollment to §G.9 default profile (SHA1 / 6 / 30 s) |
| 3 | Update verification to apply ±1 drift-window logic |
| 4 | Update all provisioning URI builders to encode default profile params |
| 5 | Update backup code logic: single-use, stored hashed, not counted as MFA |
| 6 | Update export/import: TOTP secret + profile in export, secret encrypted per §VI.4 |
| 7 | Add tests T1–T10 and static lint rules |
| 8 | Update developer docs and §VII references in onboarding material |

---

## 11. Enrollment and Verification Flow Diagrams

### 11.1 Enrollment

```
ENROLLMENT
──────────
 1. User requests MFA setup
        │
        ▼
 2. System generates TOTP secret
    (CSPRNG, ≥160 bits)
        │
        ▼
 3. Construct otpauth:// URI using §G.9:
    SHA1 / 6 digits / 30 s
        │
        ▼
 4. Display QR code + manual key to user
        │
        ▼
 5. User scans with authenticator app
        │
        ▼
 6. User enters current code → system verifies
        │
        ├── PASS → secret persisted, audit log entry
        └── FAIL → abort enrollment, show error
```

### 11.2 Verification

```
VERIFICATION
────────────
 1. User submits TOTP code
        │
        ▼
 2. System computes accepted counters:
    [T-1, T, T+1]  (T = current_unix // 30)
        │
        ▼
 3. Compare user code against each counter TOTP value
        │
        ├── MATCH found?
        │       ├── Counter in replay set? → REJECT
        │       └── No → Accept, add counter to replay set
        │
        └── No match → REJECT
```

---

## 12. Cross-References

| Reference | Location |
|-----------|----------|
| §G.9 TOTP default profile | constitution.md §G.9 |
| §VII.X Offline-Capable MFA Requirements | constitution.md §VII.X |
| §VI.4 Export Encryption Requirements | constitution.md §VI.4 |
| docs/export-encryption-spec.md | AES-256-GCM + Argon2id spec |
| checklist-totp-compliance.md | Reviewer checklist |
| RFC 6238 | https://datatracker.ietf.org/doc/html/rfc6238 |
| RFC 4226 | https://datatracker.ietf.org/doc/html/rfc4226 |
