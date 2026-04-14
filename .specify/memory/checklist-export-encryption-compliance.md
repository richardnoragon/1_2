# Export Encryption Compliance Checklist

**Applicable constitution sections**: §VI.4 (§VI.4.1–§VI.4.7), §G.7  
**Spec reference**: [docs/export-encryption-spec.md](../../docs/export-encryption-spec.md)  
**Related checklists**: [checklist-side-effect-dry-run-compliance.md](checklist-side-effect-dry-run-compliance.md)  
**Version**: 1.0 (introduced constitution v1.20.0, 2026-04-04 Q7)  

Apply this checklist to every PR that introduces or modifies:
- preference export code
- preference import code
- the export envelope format
- KDF/encryption configuration
- export-path tests

---

## Section A — Algorithm Compliance (§VI.4.1)

| # | Check | Pass / Fail |
|---|-------|-------------|
| A1 | Export uses AES-256-GCM exclusively for encrypting sensitive fields | |
| A2 | No other algorithm or mode present in the export code path (DES, RC4, AES-ECB, AES-CBC, AES-CTR alone) | |
| A3 | `encryption.algorithm` field in the exported envelope is `"aes-256-gcm"` | |
| A4 | AES key length is 256 bits (32 bytes) derived from Argon2id output | |

**FAIL conditions (any one = PR blocked)**:
- Any algorithm other than AES-256-GCM used for export encryption
- Non-AEAD mode (ECB, CBC without MAC, CTR without auth) in any export path
- `encryption.algorithm` field absent or wrong value

---

## Section B — Key Derivation Compliance (§VI.4.2)

| # | Check | Pass / Fail |
|---|-------|-------------|
| B1 | Argon2id is used as the KDF (not PBKDF2, bcrypt, scrypt, MD5, SHA-1, or direct passphrase) | |
| B2 | `memory_mb` ≥ 64 in the exported envelope | |
| B3 | `iterations` ≥ 3 in the exported envelope | |
| B4 | `parallelism` ≥ 1 in the exported envelope | |
| B5 | `salt_b64` is present and decoded length ≥ 16 bytes | |
| B6 | Salt is generated using a CSPRNG (not hardcoded, not reused) | |
| B7 | Import path validates all KDF parameter floors before decrypting | |

**FAIL conditions (any one = PR blocked)**:
- KDF is not Argon2id
- Any parameter below constitutional floor (memory < 64 MB, iters < 3, parallelism < 1, salt < 16 bytes)
- Salt is hardcoded or deterministically derived (not random)
- Import path does not validate parameter floors before use

---

## Section C — Envelope Metadata Compliance (§VI.4.3 / §G.7)

| # | Check | Pass / Fail |
|---|-------|-------------|
| C1 | `version` field present and set to `1` for new exports | |
| C2 | `encryption.algorithm` present | |
| C3 | `encryption.kdf.name` present and set to `"argon2id"` | |
| C4 | `encryption.kdf.memory_mb`, `iterations`, `parallelism` all present | |
| C5 | `encryption.kdf.salt_b64` present | |
| C6 | `encryption.nonce_b64` present (12-byte GCM nonce, base64-encoded) | |
| C7 | `encryption.tag_b64` present (16-byte GCM auth tag, base64-encoded) | |
| C8 | `meta.created_at` present (ISO 8601 UTC) | |
| C9 | `meta.schema_version` present | |
| C10 | `ciphertext_b64` present | |
| C11 | Import code validates all required fields before attempting decryption | |

**FAIL conditions (any one = PR blocked)**:
- Any required field absent from the exported envelope
- Import proceeds without validating required fields
- `version` field missing or wrong type

---

## Section D — Authentication Tag Verification (§VI.4.4)

| # | Check | Pass / Fail |
|---|-------|-------------|
| D1 | GCM auth tag verification occurs before any plaintext is used or written | |
| D2 | A failed tag verification results in import rejection with user-visible error (§G.1) | |
| D3 | No partial plaintext is accepted or written to the preference store on tag failure | |
| D4 | Error message on tag failure does NOT distinguish between wrong passphrase and tampered data | |
| D5 | Tag failure logged at WARN level (without passphrase or partial plaintext in the log) | |

**FAIL conditions (any one = PR blocked)**:
- Plaintext used or written before tag verification
- Tag failure silently accepted (no error raised)
- Partial decryption written on tag failure
- Error message leaks passphrase or plaintext

---

## Section E — Passphrase Requirement (§VI.4.5)

| # | Check | Pass / Fail |
|---|-------|-------------|
| E1 | Encryption key is derived from a user-supplied passphrase (not from a constant, config, env var, or OS keystore) | |
| E2 | No application-managed key constant (`EXPORT_KEY`, `SECRET`, etc.) present in export code | |
| E3 | Export UI prompts user for passphrase before exporting | |
| E4 | Import UI prompts user for passphrase before importing | |
| E5 | Passphrase input is masked in the UI | |
| E6 | Passphrase does NOT appear in logs, debug output, or error messages | |

**FAIL conditions (any one = PR blocked)**:
- Key derived from any source other than user passphrase
- Application-managed key constant found in export code path
- Passphrase appears in logs or debug output

---

## Section F — Test Coverage (§VI.4.7)

### F1 — Required Test Scenarios

| # | Test Scenario | Tests Present | CI Passes |
|---|---------------|---------------|-----------|
| F1a | Round-trip: correct passphrase → decrypted plaintext equals original | | |
| F1b | Wrong passphrase → import raises error, no data accepted | | |
| F1c | Tampered ciphertext → import raises error (auth tag fails) | | |
| F1d | Tampered auth tag → import raises error | | |
| F1e | Missing required envelope field → ValueError with field name | | |
| F1f | `algorithm` field is not `"aes-256-gcm"` → ValueError | | |
| F1g | `kdf.name` field is not `"argon2id"` → ValueError | | |
| F1h | `memory_mb` < 64 → ValueError | | |
| F1i | `iterations` < 3 → ValueError | | |
| F1j | `salt_b64` decoded length < 16 bytes → ValueError | | |
| F1k | Sensitive preference value present outside ciphertext → export CI scan fails | | |
| F1l | Legacy (version=0) import → succeeds + re-export notice displayed | | |

**FAIL conditions (any one = PR blocked)**:
- Any of F1a–F1k has no test coverage
- Tests are skipped, disabled, or marked `TODO`
- F1b (wrong passphrase) and F1c/F1d (tag tampering) missing — these are
  mandatory negative tests

### F2 — CI Gate Summary

| # | CI Check | Gate Failure Condition |
|---|----------|------------------------|
| F2a | Export code path uses AES-256-GCM only | Build fails if other algorithm found |
| F2b | Argon2id used with constitutional parameter floors | Build fails if floor violated |
| F2c | No app-managed key constants in export code | Build fails if hardcoded key found |
| F2d | All required envelope fields present in exported JSON | Build fails if field absent |
| F2e | No sensitive value in plaintext in export output | Build fails if leakage detected |
| F2f | Auth tag verified before plaintext used | Build fails if unverified use found |
| F2g | Wrong-passphrase test (F1b) present and passing | Build fails if absent or failing |
| F2h | Tag-tampering tests (F1c/F1d) present and passing | Build fails if absent or failing |

---

## Section G — Interoperability (§VI.4.6)

| # | Check | Pass / Fail |
|---|-------|-------------|
| G1 | Import path uses only the envelope fields to drive decryption (no implementation-specific side-channel) | |
| G2 | If additional algorithms are supported (beyond AES-256-GCM), they are extension-only; AES-256-GCM is still the default for new exports | |
| G3 | Cross-implementation round-trip test exists (export from one impl, import by another using the same envelope) | |

---

## Section H — Cross-References

| Reference | Location | Notes |
|-----------|----------|-------|
| §G.7 — Export encryption envelope | constitution.md §G.7 | Reference envelope shape |
| §VI.4 — Export Encryption Requirements | constitution.md §VI.4 | Parent normative section |
| §VI.4.1 — Mandatory algorithm (AES-256-GCM) | constitution.md §VI.4.1 | |
| §VI.4.2 — Key derivation (Argon2id floors) | constitution.md §VI.4.2 | |
| §VI.4.3 — Metadata requirements | constitution.md §VI.4.3 | |
| §VI.4.4 — Authenticated encryption | constitution.md §VI.4.4 | |
| §VI.4.5 — Passphrase requirement | constitution.md §VI.4.5 | |
| §VI.4.6 — Interoperability | constitution.md §VI.4.6 | |
| §VI.4.7 — Deterministic reviewability | constitution.md §VI.4.7 | |
| TODO(PORTABILITY_FORMAT) | constitution.md | Partially resolved in Q7; schema publication pending |
| docs/export-encryption-spec.md | docs/ | Full spec, reference implementation, CI test spec, migration plan |
| §G.1 — User-visible | constitution.md §G.1 | Required for auth-fail error display |
| §G.2 — User-discoverable | constitution.md §G.2 | Required for legacy re-export notice |
| §VI.1 — Skipped-item summary | constitution.md §VI.1 | Applied during import conflict resolution |

---

## Reviewer Sign-Off

| Reviewer | Role | Date | Signature |
|----------|------|------|-----------|
| | | | |
| | | | |

**PR MUST NOT merge if any FAIL condition in Sections A–G is unresolved.**
