# Headless HMAC Token Compliance Checklist

**Applicable constitution sections**: §G.5, §II.5 (§II.5.1–§II.5.6)
**Related checklists**: [checklist-side-effect-dry-run-compliance.md](checklist-side-effect-dry-run-compliance.md)
**Version**: 1.0 (introduced constitution v1.16.0, 2026-04-03 Q3)

---

## Purpose

This checklist is used by PR reviewers and CI gate authors to verify that any
implementation of the headless HMAC token mechanism (§G.5, §II.5) meets all
five normative attributes. Every `yes/no` item below is a constitutional
requirement. All `FAIL` conditions are PR-blocking.

---

## Scope

Apply this checklist to any PR that:
- Introduces or modifies a headless CLI execution path for a destructive operation
- Changes HMAC token issuance, validation, or redemption logic
- Changes token key storage, rotation, or key-loading behaviour
- Changes audit logging for headless token events
- Adds a new destructive operation reachable in headless mode

---

## Section A — PR Author Declaration

Before review begins, the PR author MUST declare the following:

| Item | Author answers |
|------|----------------|
| Name of the destructive operation(s) covered by this token | |
| HMAC algorithm used | |
| Key storage mechanism (name the store) | |
| Maximum token validity period (seconds or minutes) | |
| Single-use enforcement strategy (name the mechanism) | |
| Audit log destination and retention category | |

---

## Section B — Algorithm (§II.5.1)

| # | Check | Pass / Fail |
|---|-------|-------------|
| B1 | Implementation uses HMAC with SHA-256 or stronger (SHA-512 also accepted) | |
| B2 | No weaker algorithm is used or configurable (MD5, SHA-1 MUST NOT be accepted) | |
| B3 | Algorithm is not "implementation-defined" or left to a library default without explicit selection | |
| B4 | A well-maintained cryptography library is used; no homegrown HMAC implementation | |

**FAIL conditions (any one = PR blocked)**:
- MD5, SHA-1, or unspecified/default MAC is used
- Algorithm is configurable to a weaker value in production

---

## Section C — Key Storage (§II.5.2)

| # | Check | Pass / Fail |
|---|-------|-------------|
| C1 | Signing key is loaded from a secure system keystore or hardware-backed secret store (OS keyring, TPM, cloud KMS, or HSM) | |
| C2 | Signing key does NOT appear in plaintext configuration files in production | |
| C3 | Signing key does NOT appear in environment variables in production | |
| C4 | Signing key does NOT appear in source code constants or committed files | |
| C5 | Signing key does NOT appear in container environment variables in production deployments | |
| C6 | Production signing key is distinct from development and test signing keys | |
| C7 | Production and non-production keys are not shared across environments | |
| C8 | Key rotation is supported (e.g., key IDs, multiple active keys during rotation window) | |

**FAIL conditions (any one = PR blocked)**:
- Key found in .env file, config YAML/JSON, source code, or Docker env in a production path
- Production and dev/test keys are shared or identical

---

## Section D — Token Structure and Validity (§II.5.3)

| # | Check | Pass / Fail |
|---|-------|-------------|
| D1 | Token payload includes an issuance timestamp that is part of the signed (HMAC-protected) data | |
| D2 | Code enforces a hard maximum validity of ≤ 5 minutes from issuance timestamp | |
| D3 | Expiry check is mandatory and cannot be bypassed by configuration in production | |
| D4 | Minor clock skew is tolerated but the 5-minute hard upper bound is never relaxed | |
| D5 | Token is bound to a specific operation name or operation identifier | |
| D6 | Same token cannot be presented for a different operation than it was issued for | |
| D7 | Token includes caller identity or context (service account, pipeline ID, etc.) | |

**FAIL conditions (any one = PR blocked)**:
- No expiry or expiry > 5 minutes
- Expiry enforcement is "best effort" or disabled by a flag
- Same token can authorize arbitrary destructive operations (no operation binding)

---

## Section E — Single-Use Requirement (§II.5.4)

| # | Check | Pass / Fail |
|---|-------|-------------|
| E1 | After successful redemption, the token is marked as used in persistent storage | |
| E2 | A used token is rejected on a second presentation (explicit "already used" error or equivalent) | |
| E3 | The used-token store persists across process restarts (in-memory-only tracking is insufficient) | |
| E4 | If idempotency is supported it is explicit, still logged, and replay is not silently accepted | |

**FAIL conditions (any one = PR blocked)**:
- Same token can be successfully redeemed for multiple destructive operations
- Used-token tracking is in-memory only (vulnerable to process restart)

---

## Section F — Audit Logging (§II.5.5)

| # | Check | Pass / Fail |
|---|-------|-------------|
| F1 | Token **issuance** generates an audit log entry | |
| F2 | Token **redemption** (successful) generates an audit log entry | |
| F3 | Token **redemption failure** (expired, wrong op, replay, invalid sig) generates an audit log entry | |
| F4 | Issuance entry includes: timestamp, caller identity, operation name, token identifier | |
| F5 | Redemption entry includes: timestamp, caller identity, operation name, token identifier, success/failure status | |
| F6 | Failure entry includes at minimum: timestamp, operation (if known), token identifier (if parseable), failure reason | |
| F7 | Token identifier in log is a non-sensitive hash — the raw token MUST NOT appear in logs | |
| F8 | Raw key material MUST NOT appear in any log entry | |
| F9 | Audit log entries are routed to the §16 audit log and subject to the ≥ 365-day retention policy | |

**FAIL conditions (any one = PR blocked)**:
- Issuance or redemption generates no audit entry
- Full token value or raw key material appears in any log
- Audit entries bypass the §16 retention-governed log store

---

## Section G — Equivalence to Interactive Confirmation (§II.5.6)

| # | Check | Pass / Fail |
|---|-------|-------------|
| G1 | A valid §G.5-compliant token is treated as equivalent to the §II.2 interactive confirmation for the single operation it authorizes | |
| G2 | Wherever interactive confirmation is required (§II.2), headless mode ONLY proceeds after presenting a valid HMAC token that satisfies §II.5.1–§II.5.5 | |
| G3 | A plain long-form CLI flag alone does NOT satisfy the confirmation requirement | |
| G4 | The §VIII two-step typed-phrase confirmation is not required for non-anonymization destructive operations (single HMAC token is sufficient per §II opening paragraph) | |

---

## Section H — CI Enforcement Gate (Automated Checks)

The following checks MUST be automated in the CI pipeline:

| # | CI Check | Gate Failure Condition |
|---|----------|------------------------|
| H1 | Static scan: HMAC algorithm check | Any use of MD5, SHA-1, or library default MAC for headless token found in production code paths |
| H2 | Static scan: Key source check | Token signing key referenced from config file, env var, or source constant in production build |
| H3 | Unit test: Expiry — valid token | Token with `now` timestamp → accepted |
| H4 | Unit test: Expiry — expired token | Token > 5 minutes old → rejected |
| H5 | Unit test: Expiry — future timestamp | Token with far-future `iat` → rejected |
| H6 | Unit test: Single-use — first redemption | First valid redemption → succeeds |
| H7 | Unit test: Single-use — replay | Second presentation of same token → explicit "already used" failure |
| H8 | Unit test: Operation binding — correct op | Token for Op-A used on Op-A → accepted |
| H9 | Unit test: Operation binding — wrong op | Token for Op-A used on Op-B → rejected |
| H10 | Unit test: Signature tamper | Token with tampered payload → rejected |
| H11 | Unit test: Invalid signature | Token with wrong signature → rejected |
| H12 | Unit test: Unsupported algorithm | Token with unsupported algorithm → rejected |
| H13 | Audit log test: Issuance logged | Issuing a token writes an entry to the §16 audit log with required fields |
| H14 | Audit log test: Issuance — no raw token | Audit entry does not contain the raw token value or key material |
| H15 | Audit log test: Redemption logged | Successful redemption writes entry with required fields |
| H16 | Audit log test: Failure logged | Failed redemption writes entry with at minimum: timestamp, token id (if parseable), failure reason |

---

## Section I — Token Lifecycle Reference Diagram

The following lifecycle describes the normative flow for a compliant headless
HMAC token. Deviations require explicit constitutional justification.

```
+------------------+
| 1. Request Token |
| (headless client)|
+--------+---------+
         |
         v
+-----------------------------+
| 2. Issue & Sign Token       |
| - Build signed payload:     |
|   { op_id, caller, iat }    |
| - Sign with HMAC-SHA256+    |
| - key from secure keystore  |
| - Write issuance audit entry|
+--------+--------------------+
         |
         v
+-----------------------------+
| 3. Invoke Destructive Op    |
|    (headless CLI)           |
| - Client attaches token     |
+--------+--------------------+
         |
         v
+-----------------------------+
| 4. Validate Token           |
| - Verify HMAC signature     |
| - Check iat + 5min >= now   |
| - Check op_id matches       |
| - Check caller matches      |
| - Check not already used    |
+--------+--------------------+
   |               |
   | valid         | invalid
   v               v
+-------------------+    +----------------------------+
| 5a. Redeem &      |    | 5b. Reject               |
|     Execute       |    | - Write failure audit    |
| - Mark as used    |    |   entry (op if known,    |
| - Perform op      |    |   token id, reason)      |
| - Write redemption|    | - Return error           |
|   audit entry     |    +--------------------------+
+-------------------+
```

---

## Section J — Cross-References

| Reference | Location | Notes |
|-----------|----------|-------|
| §G.5 — Headless HMAC token | constitution.md §G Normative Glossary | Normative summary of all five attributes |
| §II opening paragraph | constitution.md §II | Cross-reference to §G.5 and §II.5 |
| §II.2 — Confirmation Requirement | constitution.md §II.2 | Headless token is the §II.2 equivalent in headless mode |
| §II.5.1–§II.5.6 | constitution.md §II.5 | Full normative requirements |
| §15 — Credential Reset | constitution.md §15 | §15 reset token distinct from §G.5 (see inline distinction note) |
| §16 — Session Management & Auditing | constitution.md §16 | §II.5.5 events subject to §16 ≥ 365-day retention |
| §G.4 — Destructive operation | constitution.md §G.4 | Defines the class of operations for which §G.5 applies |
| §II.3 — Internal Operations Excluded | constitution.md §II.3 | Token auditing is internal bookkeeping, but HMAC token events are part of the §16 identity/operation audit log — not excluded |
| checklist-side-effect-dry-run-compliance.md | .specify/memory/ | Section C, item C8 references HMAC headless exception |
| checklist-uiux-visibility-compliance.md | .specify/memory/ | §G.1 applies to all user-visible surfaces including token error feedback |

---

## Reviewer Sign-Off

| Reviewer | Role | Date | Signature |
|----------|------|------|-----------|
| | | | |
| | | | |

**PR MUST NOT merge if any FAIL condition in Sections B–G is unresolved.**
All Section H CI gate failures MUST be resolved before merge or documented with
an explicit time-boxed exception approved by a maintainer.
