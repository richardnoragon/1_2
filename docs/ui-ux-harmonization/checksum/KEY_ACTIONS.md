# KEY_ACTIONS — Checksum

**Tool:** Checksum  
**Source:** `src/tools/analysis/checksum/check_sum.py`  
**Constitution §7 requirement:** All key user actions reachable by keyboard; side-effect actions identified for dry-run assessment.

---

## Key Actions

| # | Action Name | Keyboard Path | Has Side Effects? |
|---|---|---|---|
| 1 | Select File | `Tab` to "Select File" button → `Enter`; file dialog opens | No — selection only |
| 2 | Choose Algorithm | `Tab` to algorithm dropdown (MD5 / SHA1 / SHA256 / SHA512) → arrow keys to change | No — configures hash method; no writes |
| 3 | Calculate Checksum | `Tab` to "Calculate" button → `Enter`; `F5` to recalculate | No — computes hash in memory; read-only |
| 4 | Copy Result to Clipboard | `Tab` to "Copy" button → `Enter` | No — copies hash string to system clipboard; no file writes |
| 5 | Verify Against Known Hash | `Tab` to verification input field → type expected hash → `Tab` to "Verify" button → `Enter` | No — comparison only; no writes |
| 6 | Batch Processing | `Tab` to "Batch" button or file list → `Enter` to run on multiple files | No — reads multiple files; no modifications |
| 7 | Refresh / Clear | `F5` | No — clears current result |
| 8 | Exit | `Ctrl+Q` | No |

### Notes

- All Checksum operations are read-only; no side effects.
- The tool may be used for security-sensitive verification (integrity checking). It is a provisional **Critical Engine candidate** (security-sensitive processing).
- `Ctrl+Q` (exit) and `F5` (refresh) confirmed in source.
