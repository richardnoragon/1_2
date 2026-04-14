# Reviewer Checklist — MFA (TOTP) Compliance
<!-- Version: 1.0 | Constitution: v1.22.0 | §VII.X, §G.9 | Q9 Applied -->

Confirm each item before marking a TOTP MFA implementation as constitutionally
compliant. All items marked **MUST** are mandatory; failure on any MUST item is
a compliance block.

---

## A. Standards Compliance

| # | Check | Status |
|---|-------|--------|
| A1 | MFA implementation uses TOTP (RFC 6238), not HOTP as the primary method | ☐ |
| A2 | HOTP is not enrolled as an active MFA method for any account | ☐ |
| A3 | If HOTP code paths exist, they are guarded so they cannot satisfy activation-gate `has_enrolled_mfa()` | ☐ |

**Fail if**: HOTP can satisfy the activation gate or is the sole enrolled method for any account.

---

## B. Default TOTP Profile (§G.9)

| # | Check | Status |
|---|-------|--------|
| B1 | Enrollment uses HMAC-SHA1 algorithm | ☐ |
| B2 | Enrollment produces 6-digit codes | ☐ |
| B3 | Enrollment uses a 30-second time step | ☐ |
| B4 | Drift tolerance is exactly ±1 time step (±30 seconds) | ☐ |
| B5 | The default profile CANNOT be globally disabled by a config flag | ☐ |
| B6 | If additional profiles (SHA-256, 8-digit, etc.) exist, they DO NOT replace the default | ☐ |

**Fail if**:
- Only SHA-256 or SHA-512 is supported (no SHA-1 path)
- Only 8-digit codes are generated
- Time step is not 30 seconds in the default path
- Drift tolerance is 0 or > ±1 step in the default path

---

## C. Enrollment Behaviour (§VII.X.3)

| # | Check | Status |
|---|-------|--------|
| C1 | TOTP secret is at least 160 bits and generated from a CSPRNG | ☐ |
| C2 | Provisioning URI uses the default profile params (SHA1, digits=6, period=30) | ☐ |
| C3 | QR code is derived from the provisioning URI | ☐ |
| C4 | Enrollment requires the user to confirm by entering one valid code | ☐ |
| C5 | TOTP secret is stored encrypted at rest (not in plaintext) | ☐ |
| C6 | Enrollment emits an audit event (`mfa_enrollment`) | ☐ |

**Fail if**:
- Provisioning URI encodes a non-default algorithm/digits/period without secondary-profile guard
- Secret is stored in plaintext

---

## D. Verification Behaviour (§VII.X.4)

| # | Check | Status |
|---|-------|--------|
| D1 | Verification checks codes for counters [T-1, T, T+1] | ☐ |
| D2 | Codes for T-2 and earlier are rejected | ☐ |
| D3 | Codes for T+2 and later are rejected | ☐ |
| D4 | A code accepted at counter C is rejected if re-submitted (replay prevention) | ☐ |
| D5 | Codes generated with non-default algorithm (e.g., SHA-256) are rejected unless that profile is explicitly configured | ☐ |
| D6 | 8-digit codes are rejected when account enrolled with 6-digit default | ☐ |

**Fail if**:
- Drift window is > ±1 step
- Replay prevention is absent
- Wrong-algorithm codes are silently accepted

---

## E. Backup and Recovery Codes (§VII.X.5)

| # | Check | Status |
|---|-------|--------|
| E1 | Backup codes, if implemented, are single-use | ☐ |
| E2 | Backup codes are stored as hashes (not plaintext) | ☐ |
| E3 | Backup code use emits an audit event (`mfa_backup_code_used`) | ☐ |
| E4 | `has_enrolled_mfa()` returns False for accounts with ONLY backup codes (no TOTP/FIDO2) | ☐ |
| E5 | Administrator is notified when a backup code is used | ☐ |

**Fail if**:
- Backup codes satisfy the activation gate check
- Backup codes are stored in plaintext

---

## F. Export and Import (§VII.X.6)

| # | Check | Status |
|---|-------|--------|
| F1 | Export payload includes TOTP secret and profile parameters | ☐ |
| F2 | TOTP secret is encrypted in export per §VI.4 (AES-256-GCM + Argon2id) | ☐ |
| F3 | Importer preserves TOTP secret and profile without alteration | ☐ |
| F4 | After import, codes generated with the default profile are accepted | ☐ |
| F5 | Import does not silently change algorithm, digits, or period to a non-constitutional value | ☐ |

**Fail if**:
- TOTP secret is exported in plaintext
- Import alters the secret or profile without an explicit legacy migration flag

---

## G. Test Coverage (§VII.X.7)

| # | Check | Test ID |
|---|-------|---------|
| G1 | Default profile interoperability test present | T1 |
| G2 | Drift tolerance — current window | T2 |
| G3 | Drift tolerance — lag window (T-30s) | T3 |
| G4 | Drift tolerance — lead window (T+30s) | T4 |
| G5 | Drift rejection — T-60s rejected | T5 |
| G6 | Drift rejection — T+60s rejected | T6 |
| G7 | Replay prevention test | T7 |
| G8 | Backup code does not satisfy enrollment check | T8 |
| G9 | HOTP account fails activation gate | T9 |
| G10 | Wrong digit length (8-digit) rejected | T10 |

**Fail if**: Any T1–T10 test is absent or failing in CI.

---

## Cross-References

| Document | Section |
|----------|---------|
| constitution.md §G.9 | TOTP default profile (normative definition) |
| constitution.md §VII.X | Offline-Capable MFA Requirements (§VII.X.1–§VII.X.7) |
| docs/totp-spec.md | Canonical spec, reference implementation, CI tests |
| docs/export-encryption-spec.md | §VI.4 encryption used for TOTP secret export |
| checklist-export-encryption-compliance.md | Export encryption checklist |
