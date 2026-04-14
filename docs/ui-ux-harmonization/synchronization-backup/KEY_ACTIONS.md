# KEY_ACTIONS — Synchronization / Backup

**Tool:** Synchronization / Backup  
**Source:** `src/tools/file_management/synchronization_backup/`  
**Constitution §7 requirement:** All key user actions reachable by keyboard; side-effect actions identified for dry-run assessment.

---

## Key Actions

| # | Action Name | Keyboard Path | Has Side Effects? |
|---|---|---|---|
| 1 | Select Source Directory | `Tab` to "Select Source" button → `Enter`; file dialog opens | No — selection only |
| 2 | Select Destination Directory | `Tab` to "Select Destination" button → `Enter`; file dialog opens | No — selection only |
| 3 | Dry Run / Preview | `Tab` to "Dry Run" or "Preview" button → `Enter` | No — simulates sync; no files written |
| 4 | Start Sync / Backup | `Tab` to "Start Sync" button → `Enter` | **Yes** — writes files to destination; may overwrite existing destination files |
| 5 | Verify Backup | `Tab` to "Verify" button → `Enter` | No — compares source and destination checksums; read-only |
| 6 | View Sync Log | `Tab` to log viewer area or log tab | No — displays previous operation results |
| 7 | Stop / Cancel | `Tab` to "Stop" or "Cancel" button → `Enter` (available during active sync) | No — halts the in-progress operation |

### Notes

- Action 4 (Start Sync) is a **Critical Engine operation** (batch, multi-file writes). A Dry Run control (Action 3) **MUST** be present and reachable before Start Sync is available (spec §5.2).
- Source: `src/tools/file_management/synchronization_backup/`; detailed button labels to be confirmed during Phase 3 assessment.
