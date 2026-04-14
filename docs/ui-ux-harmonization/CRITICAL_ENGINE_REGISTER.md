# UI/UX Harmonization — Critical Engine Register

**Version 1.1 — April 2026 (Phase 2 classifications complete)**  
**Authority:** UI/UX Harmonization Specification v0.7 §7.2 / Constitution §G.6, §III.1  
**Purpose:** Track the classification of tools and components as Critical Engines.

---

## Summary of Classifications (Phase 2)

| Classification | Tools |
|---|---|
| **Critical Engine (7)** | `synchronization_backup`, `system_cleanup`, `duplicate_finder`, `secure_delete`, `encryption`, `pdf_tools`, `file_operations` |
| **Standard (2)** | `checksum`, `security_scanner` |

---

## Classification Criteria (Constitution §G.6)

A module or component MUST be classified as a **Critical Engine** if it performs ANY of the following:

| Trigger | Description |
|---|---|
| **Batch operations** | Applies a transformation to multiple files or records in a single invoked action |
| **Irreversible operations** | Modifies or deletes data such that it cannot be restored without a backup |
| **Security-sensitive processing** | Handles encryption keys, credentials, hashes, or access-control data |
| **Multi-file writes** | Writes to more than one file as part of a single logical operation |

**Effect of classification:** Critical Engine status imposes the following in addition to standard test requirements:
- Property-based tests (e.g. Hypothesis) covering edge-case inputs
- Scenario edge tests for failure modes (partial completion, interruption, permission denied)
- Dry-run surface check must pass in CI (constitution §II.1)

---

## Classification Register

| # | Tool | Module / Component | Classification | Trigger(s) | Date classified | Notes |
|---|---|---|---|---|---|---|
| 1 | `synchronization_backup` | Sync / backup engine (`src/tools/file_management/synchronization_backup/`) | **Critical Engine** | Batch ops; multi-file writes (copies/mirrors destination tree); irreversible (overwrites/moves source files) | April 2026 | Confirmed by KEY_ACTIONS.md: Synchronize Folders, Backup Files, Restore from Backup — all multi-file writes. CE testing: property-based (large/empty dir trees) + scenario edge (partial sync, permission denied, interrupted backup). |
| 2 | `system_cleanup` | Cleanup engine (`src/tools/system/system_cleanup/`) | **Critical Engine** | Batch ops (deletes multiple temp files / empty dirs in one action); irreversible (permanent deletion, no recycle bin) | April 2026 | Confirmed by KEY_ACTIONS.md: Clean Temp Files, Remove Empty Directories. Phase 1 baseline: A11Y=25, TH=13, CP=27. CE testing: scenario edge (partial completion, locked file, permission denied). |
| 3 | `duplicate_finder` | Deduplication engine (`src/tools/analysis/duplicate_finder/`) | **Critical Engine** | Batch ops (processes multiple file groups); irreversible (deletes duplicate files) | April 2026 | Confirmed by KEY_ACTIONS.md: Delete Selected Duplicates. Phase 1 baseline: A11Y=3, TH=2, CP=3. CE testing: property-based (identical/near-identical files) + scenario edge (delete interrupted, locked file). |
| 4 | `checksum` | Hash / verification engine (`src/tools/analysis/checksum/check_sum.py`) | **Standard** | N/A | April 2026 | Source review: `calculate_checksum()` operates on a single selected file; result displayed in UI only (no writes, no deletes, no batch operations). Computes hashes for verification purposes but does NOT store, manage, or process them as security credentials or access-control data. Phase 1 baseline: A11Y=3, TH=2, CP=3. |
| 5 | `secure_delete` | Secure deletion engine (`src/tools/file_operations/secure_delete/`) | **Critical Engine** | Irreversible (multi-pass overwrite destroys file content; cannot be recovered); security-sensitive (uses cryptographic wiping algorithms — DoD 5220.22-M / Gutmann patterns); multi-file writes (writes buffers during wipe pass to each target file) | April 2026 | Confirmed by KEY_ACTIONS.md: Secure Delete File / Folder, Select Overwrite Passes. Phase 1 baseline: A11Y=7, TH=9, CP=14. CE testing: property-based (file sizes, pass counts) + scenario edge (wipe interrupted, locked file, partial completion). |
| 6 | `encryption` | Encrypt/Decrypt engine (`src/tools/security/encryption/`) | **Critical Engine** | Security-sensitive (handles encryption keys and encrypted content); irreversible on encrypt (plaintext is transformed; original not preserved unless explicitly kept); batch-capable (can encrypt multiple files) | April 2026 | Confirmed by KEY_ACTIONS.md: Encrypt File/Folder, Decrypt File/Folder. Phase 1 baseline: A11Y=7, TH=11, CP=19. CE testing: property-based (key strength, file types, size boundaries) + scenario edge (decryption with wrong key, interrupted encrypt, partial batch). |
| 7 | `security_scanner` | Security scan engine (`src/tools/security/security_scanner/security_scanner.py`) | **Standard** | N/A | April 2026 | Source review (confirmed): all four operations — `scan_system_info()`, `scan_network_ports()`, `scan_file_permissions()`, `scan_running_processes()` — are read-only. No file writes, no data deletion, no modification of access-control data. Results are displayed in UI only. Phase 1 baseline: A11Y=7, TH=6, CP=8. Note: TASKS.md §P2-T01 lists `security_scanner` as candidate #7; register previously listed "File Operations" here (discrepancy resolved — see row #9). |
| 8 | `pdf_tools` | PDF processing engine (`src/tools/pdf_tools/`) | **Critical Engine** | Batch ops (batch PDF processing across multiple input files); multi-file writes (Merge produces combined output; Split produces N outputs; Convert writes new files) | April 2026 | Confirmed by KEY_ACTIONS.md: Merge PDFs, Split PDF, Batch Process PDFs, Convert from Image, Redact PDF. Phase 1 baseline: A11Y=38+, TH=4+, CP=73 (all submodules combined). CE testing: property-based (page count, file sizes, encoding variants) + scenario edge (malformed PDF, write permission denied, merge interrupted). |
| 9 | `file_operations` | File operations engine (`src/tools/file_operations/`) | **Critical Engine** | Batch ops (copies/moves/deletes multiple files in one action); irreversible (move/delete cannot be undone without backup); multi-file writes (copy/sync writes to multiple destinations) | April 2026 | **Additional candidate** — identified during Phase 2 classification; not in original 8 provisional candidates in TASKS.md §P2-T01 but meets §G.6 criteria. Submodules: rename, file_splitter, transfer, compression, bookmarks, enhanced_clipboard, enhanced_editor. Phase 1 baseline: A11Y~170, TH~28, CP~158 (estimated; all submodules combined). CE testing: property-based (file counts, path lengths) + scenario edge (partial copy, permission denied, disk full, interrupted move). |

---

## How to Confirm or Reject a Classification

When Phase 2 Gap Analysis for a tool begins, the assessor MUST:

1. Review the tool's source for the trigger criteria above.
2. Record a decision in the `Classification` column: **Critical Engine** or **Standard**.
3. Fill in the `Trigger(s)` column with the applicable criteria (or "N/A" for Standard).
4. Record the `Date classified` and any notes.
5. If Critical Engine: confirm stricter test suites (property-based + scenario edge tests) are in the `REMEDIATION_PLAN.md`.

---

## Legend

| Value | Meaning |
|---|---|
| `Pending classification` | Not yet reviewed in Phase 2 |
| `Critical Engine` | Confirmed — stricter test requirements apply |
| `Standard` | Confirmed — standard test requirements apply |

---

*Register version 1.1. Nine entries: eight original provisional candidates (TASKS.md §P2-T01) plus one additional candidate (`file_operations`) identified during Phase 2 classification. Seven confirmed Critical Engines; two confirmed Standard. All classifications completed April 2026.*
