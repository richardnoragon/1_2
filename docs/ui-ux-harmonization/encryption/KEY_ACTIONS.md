# KEY_ACTIONS — Encryption

**Tool:** Encryption (Encrypt / Decrypt)  
**Source:** `src/tools/security/encryption/en_and_decrypt.py`  
**Constitution §7 requirement:** All key user actions reachable by keyboard; side-effect actions identified for dry-run assessment.

---

## Key Actions

| # | Action Name | Keyboard Path | Has Side Effects? |
|---|---|---|---|
| 1 | Select File(s) to Process | `Tab` to "Select Files" or file browser → `Enter`; file dialog opens | No — selection only |
| 2 | Enter Password / Key | `Tab` to password field → type passphrase | No — in-memory only |
| 3 | Choose Algorithm | `Tab` to algorithm `QComboBox` (AES-256, ChaCha20, etc.) → arrow keys | No — configuration only |
| 4 | Encrypt Files | `Tab` to "Encrypt" button → `Enter` | **Yes** — creates `.enc` copies of source files; may optionally delete originals |
| 5 | Decrypt Files | `Tab` to "Decrypt" button → `Enter` | **Yes** — decrypts `.enc` files; may overwrite plaintext originals |
| 6 | Enable Secure Delete of Originals | `Tab` to "Secure Delete Original" checkbox → `Space` to toggle | No — option only; actual deletion occurs during encrypt/decrypt |
| 7 | Batch Processing | `Tab` to file list → multi-select → apply encrypt or decrypt | **Yes** — applies encryption/decryption to multiple files with same password |
| 8 | Cancel Operation | `Tab` to "Cancel" button → `Enter` (available during active operation) | No — halts in-progress batch |

### Notes

- Actions 4, 5, and 7 are **Critical Engine operations** (security-sensitive, multi-file writes, irreversible). Confirmation dialogs MUST appear before executing (spec §5.2).
- The encrypt flow constitutes its own dry-run by nature (encryption does not delete source unless Option 6 is checked). When Option 6 is enabled, the combined encrypt + secure-delete is fully irreversible.
- Password is never logged or stored; purely in-memory during operation.
