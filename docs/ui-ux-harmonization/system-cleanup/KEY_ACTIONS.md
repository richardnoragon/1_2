# KEY_ACTIONS — System Cleanup

**Tool:** System Cleanup  
**Source:** `src/tools/system/system_cleanup/system_cleanup_gui.py`  
**Constitution §7 requirement:** All key user actions reachable by keyboard; side-effect actions identified for dry-run assessment.

---

## Key Actions

| # | Action Name | Keyboard Path | Has Side Effects? |
|---|---|---|---|
| 1 | Full System Scan | `Tab` to "Full System Scan" button → `Enter` | No — discovery scan only; no deletions |
| 2 | Quick Health Check | `Tab` to "Quick Health Check" button → `Enter` | No — read-only diagnostics |
| 3 | Preview Cleanup Targets | `Tab` to results table; review before confirming | No — displays items discovered during scan |
| 4 | Run Cleanup Programs | Context menu on selected item or "Clean" button → `Enter` | **Yes** — deletes temporary files and cache; irreversible |
| 5 | Enable Secure Delete (for temp files) | `Tab` to "Secure Delete" checkbox → `Space` to toggle | No — changes deletion method for next cleanup; no immediate writes |
| 6 | Export Report | `Tab` to "Export Report" button → `Enter` | No — writes report file to a chosen path |
| 7 | Undo Recent Cleanup | Menu callback ("Undo" in Edit menu) | Possible — may restore previously deleted items if backup available |
| 8 | Stop / Cancel Scan | `Tab` to "Stop" button → `Enter` (available during active scan) | No — cancels in-progress discovery |

### Notes

- Action 4 (Run Cleanup Programs) is a **Critical Engine operation** (batch deletions, irreversible).
- A preview/scan step (Actions 1–3) MUST precede any cleanup action, satisfying spec §5.2 dry-run requirement.
- Secure Delete checkbox (Action 5) enables multi-pass overwrite; see `secure_delete` flag in `temp_cleaner.py`.
