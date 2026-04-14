# Export Encryption Specification

**Constitutional reference**: §VI.4 (§VI.4.1–§VI.4.7), §G.7  
**Constitution version**: v1.20.0  
**Introduced**: 2026-04-04 (Round 8 — Q7)  
**Status**: Normative  

---

## 1. Purpose

This document provides the normative technical specification for the AES-256-GCM
+ Argon2id export encryption envelope required by §VI.4 of the constitution.
It covers:

- Mandatory algorithm and KDF requirements (§VI.4.1–§VI.4.2)
- Envelope structure and metadata (§VI.4.3)
- Authentication tag verification (§VI.4.4)
- Passphrase derivation rules (§VI.4.5)
- Interoperability requirements (§VI.4.6)
- CI enforcement and reviewability (§VI.4.7)
- Reference Python implementation
- CI test specification
- Migration plan for existing exports

---

## 2. Constitutional Normative Requirements

| Section  | Requirement                                             |
|----------|---------------------------------------------------------|
| §VI.4.1  | AES-256-GCM MUST be used; weaker/non-AEAD MUST NOT     |
| §VI.4.2  | Argon2id KDF; memory ≥ 64 MB, iters ≥ 3, par ≥ 1, salt ≥ 16 B |
| §VI.4.3  | Plaintext header: alg, KDF name, KDF params, salt, nonce, tag, version |
| §VI.4.4  | Auth tag MUST be verified; partial decryption MUST NOT be accepted |
| §VI.4.5  | Key MUST be passphrase-derived; app-managed keys MUST NOT be used |
| §VI.4.6  | All implementations MUST interoperate (read any conforming export) |
| §VI.4.7  | CI MUST verify alg, KDF floors, metadata, and no plaintext leakage |

---

## 3. Encryption Algorithm (§VI.4.1)

### 3.1 Required Algorithm

| Property       | Value             |
|----------------|-------------------|
| Algorithm      | AES-256-GCM       |
| Mode           | AEAD (Galois/Counter Mode) |
| Key size       | 256 bits          |
| Nonce size     | 96 bits (12 bytes) — GCM standard |
| Auth tag size  | 128 bits (16 bytes) |

AES-256-GCM provides both **confidentiality** (encryption) and **integrity**
(authentication tag). Both properties are mandatory — confidentiality without
integrity is NOT sufficient.

### 3.2 Prohibited Algorithms

The following MUST NOT be used for export encryption:

| Algorithm / Mode | Reason                              |
|-----------------|-------------------------------------|
| DES, 3DES       | Broken / insufficient key size      |
| RC4             | Broken stream cipher                |
| AES-ECB         | No semantic security (patterns leak)|
| AES-CBC         | No authentication; padding oracle   |
| AES-CTR alone   | No authentication                   |
| Any custom cipher | Not vetted; not portable          |
| Base64 / encoding | Not encryption                   |

---

## 4. Key Derivation Function (§VI.4.2)

### 4.1 Required KDF

**Argon2id** MUST be used. Argon2id is a memory-hard KDF resistant to both
GPU acceleration and side-channel attacks.

### 4.2 Minimum Parameter Floors

| Parameter    | Constitutional Minimum | Recommended Default |
|--------------|------------------------|---------------------|
| `memory`     | 64 MB                  | 64 MB               |
| `iterations` | 3                      | 3                   |
| `parallelism`| 1                      | 1                   |
| `salt`       | 16 bytes               | 16 bytes (random)   |
| `tag_length` | 32 bytes (256 bits)    | 32 bytes            |

Implementations MAY increase any parameter above the floor. They MUST NOT
fall below the floor on any parameter.

### 4.3 Salt Generation

- Salt MUST be randomly generated per export using a cryptographically secure
  random number generator (CSPRNG).
- Salt MUST NOT be reused across exports.
- Salt MUST be stored in the plaintext envelope header (§5.1).

### 4.4 Prohibited KDFs

The following MUST NOT be used:

| KDF                          | Reason                                    |
|------------------------------|-------------------------------------------|
| PBKDF2 (any iteration count) | Insufficient memory hardness              |
| bcrypt                       | Not suitable for deriving AES keys        |
| scrypt without parameter floors | Parameter-free usage is equivalent to unsupported |
| MD5/SHA-1 as KDF             | Not a KDF; trivially broken               |
| Direct passphrase as key     | No key stretching; length-dependent security |

---

## 5. Envelope Format (§VI.4.3)

### 5.1 Normative Envelope Structure

The export file MUST be a valid JSON object with the following top-level fields.
All fields except `ciphertext_b64` are plaintext.

```json
{
  "version": 1,
  "encryption": {
    "algorithm": "aes-256-gcm",
    "kdf": {
      "name": "argon2id",
      "memory_mb": 64,
      "iterations": 3,
      "parallelism": 1,
      "salt_b64": "<BASE64URL_SALT_16_BYTES_MIN>"
    },
    "nonce_b64": "<BASE64URL_NONCE_12_BYTES>",
    "tag_b64": "<BASE64URL_AUTH_TAG_16_BYTES>"
  },
  "meta": {
    "created_at": "<ISO8601_UTC_TIMESTAMP>",
    "tool": "rfu-export",
    "schema_version": "<PREFERENCE_SCHEMA_VERSION>"
  },
  "ciphertext_b64": "<BASE64URL_CIPHERTEXT>"
}
```

### 5.2 Required Fields

| Field path                         | Type   | Required | Notes |
|------------------------------------|--------|----------|-------|
| `version`                          | int    | YES      | Must be `1` for this spec; increment for future envelope versions |
| `encryption.algorithm`             | string | YES      | Must be `"aes-256-gcm"` |
| `encryption.kdf.name`              | string | YES      | Must be `"argon2id"` |
| `encryption.kdf.memory_mb`         | int    | YES      | Must be ≥ 64 |
| `encryption.kdf.iterations`        | int    | YES      | Must be ≥ 3 |
| `encryption.kdf.parallelism`       | int    | YES      | Must be ≥ 1 |
| `encryption.kdf.salt_b64`          | string | YES      | Base64-encoded; decoded length ≥ 16 bytes |
| `encryption.nonce_b64`             | string | YES      | Base64-encoded; 12 bytes for GCM |
| `encryption.tag_b64`               | string | YES      | Base64-encoded; 16 bytes for GCM-128 |
| `meta.created_at`                  | string | YES      | ISO 8601 UTC |
| `meta.schema_version`              | string | YES      | Preference schema version string |
| `ciphertext_b64`                   | string | YES      | Base64-encoded AES-256-GCM ciphertext |

### 5.3 Sensitive Data Boundary

All sensitive preference values — every key with `sensitive=True` in the
preference registry — MUST reside exclusively inside `ciphertext_b64`.

No sensitive value MAY appear:
- In any plaintext field of the envelope
- In `meta` values
- In intermediate log output
- In error messages

### 5.4 Version Semantics

| `version` | Meaning                                      |
|-----------|----------------------------------------------|
| `0`       | Legacy / pre-v1.20.0 format (import-only)    |
| `1`       | AES-256-GCM + Argon2id (this spec; v1.20.0+) |
| `2+`      | Reserved for future algorithm migrations     |

---

## 6. Authentication Tag Verification (§VI.4.4)

### 6.1 Import Verification Requirement

When importing an export envelope:

1. Parse the envelope JSON and extract all metadata fields.
2. Derive the decryption key from the user-supplied passphrase using the
   KDF parameters in `encryption.kdf`.
3. Attempt AES-256-GCM decryption with the nonce in `encryption.nonce_b64`.
4. **Verify the authentication tag** (`encryption.tag_b64`) as part of
   decryption. Most AES-GCM implementations do this automatically.
5. **ONLY if tag verification succeeds**: accept the plaintext and continue.
6. **If tag verification fails**: reject the import entirely. Do NOT accept
   or display any partial decryption output.

### 6.2 Tag Failure Handling

A tag verification failure MUST:

- Produce a user-visible error message indicating that the export could not
  be authenticated (§G.1).
- NOT reveal whether the failure was caused by a wrong passphrase, data
  tampering, or file corruption (avoid oracle attacks).
- NOT write any data to the preference store.
- Log the failure event at WARN level (component, timestamp, failure type
  — without the passphrase or any partial plaintext).

---

## 7. Passphrase Requirement (§VI.4.5)

### 7.1 Key Source Rules

| Key source              | Permitted? | Reason |
|-------------------------|-----------|--------|
| User-supplied passphrase (interactive) | YES | Passphrase-derived per §VI.4.5 |
| User-supplied passphrase (CLI `--passphrase` flag) | YES | Passphrase-derived |
| Application constant / hard-coded key | NO  | Not user-controlled; not portable |
| Config file key         | NO         | Same filesystem as ciphertext |
| Environment variable key | NO        | Accessible to all processes |
| OS keychain / keystore  | NO         | Not portable to other devices |

### 7.2 Passphrase UX Requirements

- The export UI MUST prompt the user to supply a passphrase before exporting.
- The import UI MUST prompt the user to supply the passphrase used at export
  time.
- Passphrase input MUST be masked in the UI.
- Passphrase MUST NOT be echoed in logs, debug output, or error messages.

---

## 8. Interoperability (§VI.4.6)

### 8.1 Cross-Implementation Requirement

Any implementation conforming to §VI.4 MUST be able to decrypt an export
envelope produced by any other conforming implementation. The envelope format
defined in §5.1 is the interoperability contract.

### 8.2 Additional Algorithm Support

An implementation MAY support decryption of:
- Legacy (version: 0) exports for backward compatibility
- Other AEAD algorithms (e.g., ChaCha20-Poly1305) as optional extensions

When supporting additional algorithms, the implementation MUST:
- Use the `encryption.algorithm` field to select the decryption path
- Still use AES-256-GCM for all new exports
- NOT treat the additional-algorithm path as a substitute for the
  constitutional minimum

### 8.3 Legacy Import Behavior

When importing a version-0 (legacy) export:
- Import as before (using the legacy format's own decryption mechanism,
  if any)
- After a successful legacy import, prompt the user to re-export using
  the new envelope format
- Display a user-discoverable notice (§G.2) that the legacy format is
  deprecated

---

## 9. Reference Implementation (Python)

### 9.1 Dependencies

```python
# Requirements (add to requirements.txt):
# argon2-cffi >= 21.3.0
# cryptography >= 41.0.0
```

### 9.2 Export

```python
import json
import os
import base64
from datetime import datetime, timezone
from argon2.low_level import hash_secret_raw, Type
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Constitutional minimum parameters (§VI.4.2)
ARGON2_MEMORY_MB  = 64    # minimum: 64 MB
ARGON2_ITERATIONS = 3     # minimum: 3
ARGON2_PARALLELISM = 1    # minimum: 1
ARGON2_SALT_BYTES = 16    # minimum: 16 bytes
ARGON2_TAG_BYTES  = 32    # 256-bit derived key
GCM_NONCE_BYTES   = 12    # GCM standard: 96-bit nonce


def export_preferences(
    plaintext: bytes,
    passphrase: str,
    schema_version: str,
) -> str:
    """
    Encrypt preference export data using AES-256-GCM + Argon2id.
    Returns the envelope as a JSON string.

    plaintext: serialized preference data (JSON or structured bytes)
    passphrase: user-supplied passphrase (never stored)
    schema_version: current preference schema version string
    """
    # 1. Generate random salt and nonce
    salt  = os.urandom(ARGON2_SALT_BYTES)
    nonce = os.urandom(GCM_NONCE_BYTES)

    # 2. Derive key via Argon2id (§VI.4.2)
    key = hash_secret_raw(
        secret=passphrase.encode("utf-8"),
        salt=salt,
        time_cost=ARGON2_ITERATIONS,
        memory_cost=ARGON2_MEMORY_MB * 1024,  # argon2-cffi uses KiB
        parallelism=ARGON2_PARALLELISM,
        hash_len=ARGON2_TAG_BYTES,
        type=Type.ID,  # Argon2id
    )

    # 3. Encrypt with AES-256-GCM (§VI.4.1)
    aesgcm = AESGCM(key)
    ciphertext_with_tag = aesgcm.encrypt(nonce, plaintext, associated_data=None)
    # cryptography separates tag at the end (last 16 bytes)
    ciphertext = ciphertext_with_tag[:-16]
    tag        = ciphertext_with_tag[-16:]

    # 4. Build envelope (§VI.4.3 / §G.7)
    envelope = {
        "version": 1,
        "encryption": {
            "algorithm": "aes-256-gcm",
            "kdf": {
                "name": "argon2id",
                "memory_mb": ARGON2_MEMORY_MB,
                "iterations": ARGON2_ITERATIONS,
                "parallelism": ARGON2_PARALLELISM,
                "salt_b64": base64.b64encode(salt).decode(),
            },
            "nonce_b64": base64.b64encode(nonce).decode(),
            "tag_b64":   base64.b64encode(tag).decode(),
        },
        "meta": {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "tool": "rfu-export",
            "schema_version": schema_version,
        },
        "ciphertext_b64": base64.b64encode(ciphertext).decode(),
    }
    return json.dumps(envelope, indent=2)
```

### 9.3 Import

```python
def import_preferences(
    envelope_json: str,
    passphrase: str,
) -> bytes:
    """
    Decrypt a preference export envelope.
    Returns the plaintext preference bytes.
    Raises ValueError on any authentication or format failure.

    passphrase: user-supplied passphrase (never stored)
    """
    try:
        envelope = json.loads(envelope_json)
    except json.JSONDecodeError as exc:
        raise ValueError("Export file is not valid JSON") from exc

    # Validate required fields
    _validate_envelope_fields(envelope)

    enc = envelope["encryption"]
    kdf = enc["kdf"]

    # Validate constitutional minimums (§VI.4.2)
    if kdf["memory_mb"] < 64:
        raise ValueError("KDF memory below constitutional minimum (64 MB)")
    if kdf["iterations"] < 3:
        raise ValueError("KDF iterations below constitutional minimum (3)")
    if kdf["parallelism"] < 1:
        raise ValueError("KDF parallelism below constitutional minimum (1)")

    salt      = base64.b64decode(kdf["salt_b64"])
    nonce     = base64.b64decode(enc["nonce_b64"])
    tag       = base64.b64decode(enc["tag_b64"])
    ciphertext = base64.b64decode(envelope["ciphertext_b64"])

    if len(salt) < 16:
        raise ValueError("Salt below constitutional minimum (16 bytes)")

    # Derive key
    key = hash_secret_raw(
        secret=passphrase.encode("utf-8"),
        salt=salt,
        time_cost=kdf["iterations"],
        memory_cost=kdf["memory_mb"] * 1024,
        parallelism=kdf["parallelism"],
        hash_len=32,
        type=Type.ID,
    )

    # Decrypt + verify auth tag (§VI.4.4)
    aesgcm = AESGCM(key)
    ciphertext_with_tag = ciphertext + tag
    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext_with_tag, associated_data=None)
    except Exception as exc:
        # Do NOT reveal whether failure is wrong passphrase or tampered data
        raise ValueError(
            "Export authentication failed: the file could not be verified. "
            "Check the passphrase or the integrity of the export file."
        ) from exc

    return plaintext


def _validate_envelope_fields(envelope: dict) -> None:
    required_paths = [
        ("version",),
        ("encryption", "algorithm"),
        ("encryption", "kdf", "name"),
        ("encryption", "kdf", "memory_mb"),
        ("encryption", "kdf", "iterations"),
        ("encryption", "kdf", "parallelism"),
        ("encryption", "kdf", "salt_b64"),
        ("encryption", "nonce_b64"),
        ("encryption", "tag_b64"),
        ("meta", "created_at"),
        ("meta", "schema_version"),
        ("ciphertext_b64",),
    ]
    for path in required_paths:
        obj = envelope
        for key in path:
            if not isinstance(obj, dict) or key not in obj:
                raise ValueError(f"Missing required envelope field: {'.'.join(path)}")
            obj = obj[key]
    if envelope["encryption"]["algorithm"] != "aes-256-gcm":
        raise ValueError(
            f"Unsupported algorithm: {envelope['encryption']['algorithm']!r}. "
            "Only 'aes-256-gcm' is supported."
        )
    if envelope["encryption"]["kdf"]["name"] != "argon2id":
        raise ValueError(
            f"Unsupported KDF: {envelope['encryption']['kdf']['name']!r}. "
            "Only 'argon2id' is supported."
        )
```

---

## 10. CI Test Specification (§VI.4.7)

### 10.1 Required Tests

| ID  | Test Scenario                          | Assertion |
|-----|----------------------------------------|-----------|
| T1  | Round-trip: export + import with correct passphrase | Decrypted plaintext equals original |
| T2  | Wrong passphrase                       | Import raises error; no data accepted |
| T3  | Tampered ciphertext                    | Import raises error (auth tag fails) |
| T4  | Tampered auth tag                      | Import raises error |
| T5  | Missing required envelope field        | Import raises ValueError listing the missing field |
| T6  | Algorithm field is not "aes-256-gcm"   | Import raises ValueError |
| T7  | KDF field is not "argon2id"            | Import raises ValueError |
| T8  | memory_mb below floor (< 64)           | Import raises ValueError |
| T9  | iterations below floor (< 3)           | Import raises ValueError |
| T10 | salt length below floor (< 16 bytes)   | Import raises ValueError |
| T11 | Sensitive field present outside ciphertext | Export raises error / CI scan fails |
| T12 | Legacy (version=0) import              | Import succeeds; user receives re-export notice |
| T13 | Cross-implementation round-trip        | Export from impl A; import by impl B succeeds |

### 10.2 CI Enforcement Rules

| Rule | Description                                                | Failure |
|------|------------------------------------------------------------|---------|
| R1   | Export code path uses only AES-256-GCM                     | Build fails |
| R2   | Argon2id used with parameter floors on all export paths    | Build fails |
| R3   | No application-managed key constant in export code         | Build fails |
| R4   | All required envelope fields present in exported JSON      | Build fails |
| R5   | No sensitive preference value appears in plaintext in export output | Build fails |
| R6   | Auth tag verified before plaintext used in import          | Build fails |
| R7   | Wrong-passphrase test (T2) present and passing             | Build fails |
| R8   | Tag-tampering test (T3/T4) present and passing             | Build fails |

---

## 11. Migration Plan

### Step 1 — Inventory Existing Export Formats

Identify all existing export code paths. For each:
- Document whether it is encrypted, plaintext, or partially obscured.
- Tag as `version: 0` (legacy).

### Step 2 — Introduce Version Field

Add `"version": 0` to any existing export format that does not already have
it. This enables the importer to branch on format.

### Step 3 — New Exports Use the Envelope

Change all export code to use the `export_preferences()` function in §9.2:
- Prompt user for passphrase.
- Derive key via Argon2id.
- Encrypt with AES-256-GCM.
- Emit the v1 envelope JSON.

### Step 4 — Import Supports Both Formats

On import, branch on `version`:
- `version: 1` → use `import_preferences()` from §9.3.
- `version: 0` or missing → use legacy import path.
- After successful legacy import, display a user-discoverable notice (§G.2):
  *"This export uses a legacy format. Please re-export to upgrade the
  encryption."*

### Step 5 — Deprecate Legacy Exports

- Mark v0 export paths as deprecated in code comments and user docs.
- Remove v0 export generation in a future minor version (announce in changelog).
- v0 import support MAY be retained indefinitely for user data safety.

### Step 6 — Add Tests and Update Docs

- Add T1–T13 from §10.1 to the test suite.
- Update user-facing documentation to describe:
  - Passphrase requirement.
  - Envelope format.
  - Migration behavior for legacy exports.

---

## 12. Migration Tracker

| Module / Exporter | Current Format | Migrated to v1 | Tests (T1–T13) | Notes |
|-------------------|----------------|----------------|----------------|-------|
| *(new exporters post-v1.20.0 are in-scope from creation)* | | | | |

---

## 13. Cross-References

| Reference                              | Location                                        |
|----------------------------------------|-------------------------------------------------|
| §G.7 — Export encryption envelope      | constitution.md §G.7                            |
| §VI.4 — Export Encryption Requirements | constitution.md §VI.4                           |
| §VI.4.1 — Mandatory algorithm          | constitution.md §VI.4.1                         |
| §VI.4.2 — Key derivation floors        | constitution.md §VI.4.2                         |
| §VI.4.3 — Metadata requirements        | constitution.md §VI.4.3                         |
| §VI.4.4 — Authenticated encryption     | constitution.md §VI.4.4                         |
| §VI.4.5 — Passphrase requirement       | constitution.md §VI.4.5                         |
| §VI.4.6 — Interoperability             | constitution.md §VI.4.6                         |
| §VI.4.7 — Deterministic reviewability  | constitution.md §VI.4.7                         |
| TODO(PORTABILITY_FORMAT)               | constitution.md — partially resolved (v1.20.0); schema publication still pending |
| Reviewer checklist                     | .specify/memory/checklist-export-encryption-compliance.md |
| §G.4 — Destructive operation           | constitution.md §G.4                            |
| §II.1 — Dry-run                        | constitution.md §II.1                           |
| §VI.1 — Skipped-item summary           | constitution.md §VI.1                           |
