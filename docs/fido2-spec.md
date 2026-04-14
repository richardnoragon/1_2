# FIDO2 Authenticator Specification — Offline-Capable MFA
<!-- Version: 1.0 | Constitution: v1.23.0 | Q10 Applied -->

## 1. Purpose

This document is the canonical specification for FIDO2 MFA in RFU. It
prescribes authenticator classification (roaming vs platform), enrollment and
verification requirements, pairing rules, recovery rules, export/import
behaviour, UI labelling requirements, and CI enforcement criteria.

**Constitutional authority**: §VII.Y (§VII.Y.1–§VII.Y.6) and §G.10.

---

## 2. Governing Standards

| Item | Value |
|------|-------|
| Primary standard | FIDO2 / WebAuthn (W3C Web Authentication Level 2) |
| Underlying protocol | CTAP2 (Client to Authenticator Protocol 2) |
| Roaming authenticators | `authenticatorAttachment = "cross-platform"` |
| Platform authenticators | `authenticatorAttachment = "platform"` |

---

## 3. Authenticator Classification (§G.10)

### 3.1 FIDO2 Roaming Authenticator

A **FIDO2 roaming authenticator** is a physically detachable hardware device
(YubiKey, Titan Key, Feitian, etc.) that:

- connects via USB-A, USB-C, NFC, or BLE
- is not bound to a specific host device
- can be used on any number of devices
- stores FIDO2 credentials in its own secure element

**Status**: Satisfies the offline-capable MFA enrollment requirement (§VII.Y.2).

### 3.2 FIDO2 Platform Authenticator

A **FIDO2 platform authenticator** is a device-bound authenticator integrated
into the host (Windows Hello, Apple Touch ID / Face ID, Android biometric,
TPM-backed keys) that:

- is bound to a specific device
- cannot be transferred to a replacement device
- credentials are lost if the device is lost, wiped, or replaced

**Status**: Does **not** satisfy the offline-capable MFA enrollment requirement
when enrolled alone. MAY be enrolled as a convenience factor provided the
pairing rule in §3.3 / §VII.Y.3 is met.

### 3.3 Pairing Rule

If and only if a platform authenticator is the user's sole FIDO2 enrollment,
the implementation MUST ensure the user also has:

- a FIDO2 roaming authenticator enrolled, **or**
- a TOTP method enrolled per §VII.X / §G.9.

An account with **only** a platform authenticator enrolled MUST NOT be
considered MFA-complete for activation-gate purposes.

---

## 4. Enrollment Requirements (§VII.Y.3, §VII.Y.5)

1. **Detect attachment type**: read `authenticatorAttachment` from the
   WebAuthn credential creation response.
2. **Store attachment type** alongside the credential in the database
   (`attachment: "cross-platform" | "platform"`).
3. **Update user MFA status**:
   - `cross-platform` credential → `has_roaming_fido2 = true`
   - `platform` credential → `has_platform_fido2 = true`
4. **Enforce pairing rule**: after enrollment, evaluate:
   ```
   mfa_complete = has_roaming_fido2 OR has_totp
   ```
   If `mfa_complete = false` (only platform enrolled), set
   `mfa_status = "incomplete_platform_only"` and prompt the user to add a
   security key or TOTP.
5. **UI labelling** (§VII.Y.5):
   - Display `"cross-platform"` credentials as **"Security Key"**.
   - Display `"platform"` credentials as **"This Device"**.
   - MUST NOT use the label "hardware token" for platform credentials.
6. **Emit audit entry**: `mfa_enrollment` with `attachment` field and
   timestamp.

---

## 5. Verification Requirements

1. Challenge generation: generate a fresh random challenge (≥ 128 bits) for
   every assertion request.
2. Origin and RP ID validation: MUST verify `origin` and `rpId` match the
   application's registered values.
3. User Presence (UP): MUST verify the UP bit is set in the authenticator data.
4. User Verification (UV): UV is **preferred**; enforcement is
   implementation-defined per deployment security policy, but MUST be
   documented.
5. Signature counter: MUST track the signature counter and reject credentials
   where the counter value is lower than or equal to the previously stored
   value (indicates cloned or replayed credential).

---

## 6. Recovery and Portability (§VII.Y.4)

- **Platform credentials MUST NOT be exported** as portable artifacts in any
  export workflow.
- Export payloads for MFA configuration MUST include roaming authenticator
  metadata only (credential ID, public key, device name/label, enrolled_at).
- Implementations MUST ensure a recovery path exists via a roaming
  authenticator or TOTP if the user's platform device is lost:
  - Admin-performed MFA reset (see §VII MFA recovery path) is the fallback
    when all portable methods are also lost.
  - The admin reset MUST require the admin to pass their own MFA challenge.

---

## 7. Export Record Shape (Roaming Authenticator Only)

```json
{
  "mfa_type": "fido2_roaming",
  "attachment": "cross-platform",
  "credential_id": "<base64url>",
  "public_key": "<base64url COSE key>",
  "label": "YubiKey 5 NFC",
  "enrolled_at": "<ISO-8601 timestamp>",
  "account_id": "<UUID>"
}
```

Platform authenticator credentials MUST NOT appear in this record shape and
MUST NOT be exported.

---

## 8. Reference Implementation (WebAuthn Pseudocode — Python-style)

```python
"""
fido2_reference.py — Constitutional FIDO2 enrollment enforcement
Standard: WebAuthn L2  |  Constitution: §VII.Y, §G.10  |  Spec: docs/fido2-spec.md
"""

from dataclasses import dataclass
from enum import Enum


class Attachment(str, Enum):
    ROAMING = "cross-platform"
    PLATFORM = "platform"


@dataclass
class Fido2Credential:
    credential_id: str
    public_key: bytes
    attachment: Attachment
    account_id: str
    label: str


def register_fido2_credential(
    user,
    credential: Fido2Credential,
    db,
    audit_log,
) -> dict:
    """
    Persist a FIDO2 credential and evaluate MFA completeness.
    Returns {"mfa_complete": bool, "status": str}.
    """
    # Persist credential with attachment type
    db.save_credential(credential)

    # Update user MFA flags
    if credential.attachment == Attachment.ROAMING:
        db.set_user_flag(user.id, "has_roaming_fido2", True)
    else:
        db.set_user_flag(user.id, "has_platform_fido2", True)

    # Evaluate MFA completeness (§VII.Y.3 pairing rule)
    has_roaming = db.get_user_flag(user.id, "has_roaming_fido2")
    has_totp = db.get_user_flag(user.id, "has_totp")
    mfa_complete = has_roaming or has_totp

    status = "complete" if mfa_complete else "incomplete_platform_only"
    db.set_user_mfa_status(user.id, status)

    # Emit audit entry
    audit_log.record(
        event="mfa_enrollment",
        account_id=user.id,
        attachment=credential.attachment.value,
        mfa_status=status,
    )

    return {"mfa_complete": mfa_complete, "status": status}


def has_enrolled_mfa(user, db) -> bool:
    """
    Returns True only if the user has at least one offline-capable MFA method.
    Platform-only does NOT satisfy this check.
    """
    return db.get_user_flag(user.id, "has_roaming_fido2") or \
           db.get_user_flag(user.id, "has_totp")


def ui_label_for_credential(credential: Fido2Credential) -> str:
    """Return the constitutional UI label for a credential (§VII.Y.5)."""
    if credential.attachment == Attachment.ROAMING:
        return "Security Key"
    return "This Device"


def export_mfa_config(user, db) -> list:
    """
    Export MFA configuration. Platform credentials MUST NOT be exported.
    """
    credentials = db.get_credentials(user.id)
    return [
        {
            "mfa_type": "fido2_roaming",
            "attachment": "cross-platform",
            "credential_id": cred.credential_id,
            "public_key": cred.public_key.hex(),
            "label": cred.label,
            "account_id": user.id,
        }
        for cred in credentials
        if cred.attachment == Attachment.ROAMING
        # Platform credentials explicitly excluded
    ]
```

---

## 9. CI Test Specification (§VII.Y.6)

### 9.1 Unit Tests

| ID | Name | Pass condition |
|----|------|----------------|
| T1 | Roaming enrollment satisfies MFA requirement | `has_enrolled_mfa()` returns `True` after roaming credential enrolled |
| T2 | Platform-only enrollment does NOT satisfy requirement | `has_enrolled_mfa()` returns `False` after only platform credential enrolled |
| T3 | Platform + roaming satisfies requirement | `has_enrolled_mfa()` returns `True` after both enrolled |
| T4 | Platform + TOTP satisfies requirement | `has_enrolled_mfa()` returns `True` when TOTP enrolled alongside platform |
| T5 | UI label — roaming | `ui_label_for_credential(roaming_cred)` returns `"Security Key"` |
| T6 | UI label — platform | `ui_label_for_credential(platform_cred)` returns `"This Device"` |
| T7 | Export excludes platform credentials | `export_mfa_config()` contains no `"platform"` entries |

### 9.2 Integration Tests

| ID | Name | Pass condition |
|----|------|----------------|
| T8 | Cross-device authentication | Credential enrolled on Device A accepted on Device B (roaming) |
| T9 | Platform credential rejected cross-device | Platform credential enrolled on Device A rejected on Device B |
| T10 | Device-loss simulation | Platform-only user cannot authenticate after device is wiped; admin reset path available |

### 9.3 Static Analysis Rules

CI MUST detect and reject:
- Any code path where a `"platform"` attachment is treated as satisfying
  `has_enrolled_mfa()`
- Any code path that labels a platform credential as `"hardware token"`
- Any export flow that includes `attachment = "platform"` credentials

### 9.4 CI Failure Conditions

CI MUST fail if any of the following are true:
- Platform authenticators can satisfy `has_enrolled_mfa()` alone
- Roaming vs platform attachment is not stored per credential
- UI labelling tests (T5, T6) are absent or failing
- Export includes platform credentials (T7 failing)
- T1–T4 tests are absent or failing
- No recovery-path test for platform-only account (T10 absent or failing)

---

## 10. Migration Plan for Existing FIDO2 Implementations

| Step | Action |
|------|--------|
| 1 | Audit all existing FIDO2 credential records; add `attachment` column if absent |
| 2 | Back-fill `attachment` for existing credentials (default to `"cross-platform"` if unknown, flag for review) |
| 3 | Update `has_enrolled_mfa()` to check `has_roaming_fido2 OR has_totp` only |
| 4 | Update enrollment flow to read and store `authenticatorAttachment` from WebAuthn response |
| 5 | Add platform-pairing enforcement: set `mfa_status = "incomplete_platform_only"` and prompt user |
| 6 | Update UI labels: "Security Key" / "This Device" per §VII.Y.5 |
| 7 | Update export logic to exclude platform credentials; update export tests |

---

## 11. Enrollment Flow Diagram

```
FIDO2 ENROLLMENT
────────────────
 1. User initiates FIDO2 enrollment
        │
        ▼
 2. Server generates challenge (≥128 bits random)
    Server sends PublicKeyCredentialCreationOptions
    (attachment: "cross-platform" or "platform")
        │
        ▼
 3. Authenticator creates credential
    User interacts with device (tap, biometric)
        │
        ▼
 4. Browser returns PublicKeyCredential
    Server reads `authenticatorAttachment` field
        │
        ▼
 5. Server verifies attestation
    Stores credential with attachment type
        │
        ▼
 6. Server evaluates pairing rule (§VII.Y.3)
    mfa_complete = has_roaming OR has_totp?
        │
        ├── YES → mfa_status = "complete"
        │          Audit entry emitted
        │
        └── NO (platform only)
               │
               ▼
           mfa_status = "incomplete_platform_only"
           UI prompts: "Add a Security Key or TOTP"
```

---

## 12. Cross-References

| Reference | Location |
|-----------|----------|
| §G.10 FIDO2 authenticator classes | constitution.md §G.10 |
| §VII.Y FIDO2 Authenticator Requirements | constitution.md §VII.Y |
| §VII.X Offline-Capable MFA Requirements | constitution.md §VII.X |
| §G.9 TOTP default profile | constitution.md §G.9 |
| docs/totp-spec.md | TOTP canonical spec |
| checklist-fido2-compliance.md | Reviewer checklist |
| W3C WebAuthn Level 2 | https://www.w3.org/TR/webauthn-2/ |
| CTAP2 specification | https://fidoalliance.org/specs/fido-v2.0-id-20180227/fido-client-to-authenticator-protocol-v2.0-id-20180227.html |
