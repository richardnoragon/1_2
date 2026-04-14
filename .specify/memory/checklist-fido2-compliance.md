# Reviewer Checklist — FIDO2 Compliance
<!-- Version: 1.0 | Constitution: v1.23.0 | §VII.Y, §G.10 | Q10 Applied -->

Confirm each item before marking a FIDO2 MFA implementation as constitutionally
compliant. All items marked **MUST** are mandatory; failure on any MUST item is
a compliance block.

---

## A. Terminology & Classification

| # | Check | Status |
|---|-------|--------|
| A1 | Code explicitly distinguishes `"cross-platform"` (roaming) from `"platform"` credentials | ☐ |
| A2 | `attachment` field is stored per credential in the database | ☐ |
| A3 | The term "FIDO2 hardware token" is NOT used for platform authenticators anywhere in code, UI, or docs | ☐ |
| A4 | §G.10 definitions are reflected in code variable/constant names (e.g., `Attachment.ROAMING`, `Attachment.PLATFORM`) | ☐ |

**Fail if**: Platform authenticators are labelled "hardware token" or attachment type is not stored.

---

## B. Enrollment — MFA Completeness Enforcement (§VII.Y.2, §VII.Y.3)

| # | Check | Status |
|---|-------|--------|
| B1 | `has_enrolled_mfa()` returns `True` only when `has_roaming_fido2 OR has_totp` | ☐ |
| B2 | `has_enrolled_mfa()` returns `False` when only a platform credential is enrolled | ☐ |
| B3 | After platform-only enrollment, `mfa_status` is set to `"incomplete_platform_only"` (or equivalent) | ☐ |
| B4 | User is prompted to add a Security Key or TOTP when `mfa_status = "incomplete_platform_only"` | ☐ |
| B5 | Enrollment emits an audit event (`mfa_enrollment`) including `attachment` type and timestamp | ☐ |

**Fail if**: B1 or B2 evaluates incorrectly — platform-only account must not pass the activation gate.

---

## C. Pairing Rule (§VII.Y.3)

| # | Check | Status |
|---|-------|--------|
| C1 | An account with ONLY a platform credential cannot have `account_status = active` | ☐ |
| C2 | Enrolling a roaming key alongside an existing platform credential upgrades status to `"complete"` | ☐ |
| C3 | Enrolling TOTP alongside an existing platform credential upgrades status to `"complete"` | ☐ |
| C4 | Unenrolling the last roaming key from a platform-only-remaining account sets status to `"incomplete_platform_only"` | ☐ |

**Fail if**: Any path allows activation with only a platform credential.

---

## D. Recovery and Portability (§VII.Y.4)

| # | Check | Status |
|---|-------|--------|
| D1 | Platform credentials are excluded from all export workflows | ☐ |
| D2 | Export payloads contain only `"cross-platform"` credential records | ☐ |
| D3 | A recovery path exists for a user who loses their platform device (admin MFA reset) | ☐ |
| D4 | Admin MFA reset requires the admin to pass their own MFA challenge (existing §VII requirement) | ☐ |
| D5 | Documentation for device-loss recovery is present | ☐ |

**Fail if**: D1 or D2 fails (platform credentials must never be exported).

---

## E. UI / UX Labelling (§VII.Y.5)

| # | Check | Status |
|---|-------|--------|
| E1 | Roaming (`cross-platform`) credentials are labelled **"Security Key"** (or equivalent non-ambiguous label) | ☐ |
| E2 | Platform credentials are labelled **"This Device"** (or equivalent) | ☐ |
| E3 | No UI element labels a platform credential as "hardware token", "security key", or implies portability | ☐ |
| E4 | Enrollment flow identifies the type of authenticator before or during registration | ☐ |

**Fail if**: E1, E2, or E3 fails.

---

## F. Export and Import (§VII.Y.4, §VII.Y.6)

| # | Check | Status |
|---|-------|--------|
| F1 | Export record contains `"mfa_type": "fido2_roaming"` and `"attachment": "cross-platform"` | ☐ |
| F2 | No `"platform"` attachment records present in export payload | ☐ |
| F3 | Import restores roaming credential metadata correctly | ☐ |
| F4 | Import does not accept or process platform credential exports | ☐ |

**Fail if**: F1 or F2 fails.

---

## G. Test Coverage (§VII.Y.6)

| # | Check | Test ID |
|---|-------|---------|
| G1 | Roaming enrollment satisfies MFA requirement | T1 |
| G2 | Platform-only enrollment does NOT satisfy requirement | T2 |
| G3 | Platform + roaming satisfies requirement | T3 |
| G4 | Platform + TOTP satisfies requirement | T4 |
| G5 | UI label: roaming → "Security Key" | T5 |
| G6 | UI label: platform → "This Device" | T6 |
| G7 | Export excludes platform credentials | T7 |
| G8 | Cross-device roaming authentication succeeds | T8 |
| G9 | Platform credential rejected cross-device | T9 |
| G10 | Device-loss simulation: platform-only user cannot authenticate | T10 |

**Fail if**: Any T1–T7 test is absent or failing. T8–T10 absence is a compliance warning; absence in production-class implementations is a compliance block.

---

## Cross-References

| Document | Section |
|----------|---------|
| constitution.md §G.10 | FIDO2 authenticator classes (normative definitions) |
| constitution.md §VII.Y | FIDO2 Authenticator Requirements (§VII.Y.1–§VII.Y.6) |
| constitution.md §VII.X | Offline-Capable MFA Requirements (TOTP) |
| constitution.md §G.9 | TOTP default profile |
| docs/fido2-spec.md | Canonical FIDO2 spec, reference implementation, CI tests |
| docs/totp-spec.md | TOTP spec (for pairing rule TOTP side) |
| checklist-totp-compliance.md | TOTP compliance checklist |
