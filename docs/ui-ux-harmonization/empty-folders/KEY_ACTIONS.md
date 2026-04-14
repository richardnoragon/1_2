# KEY_ACTIONS — Empty Folders

**Tool:** Empty Folders  
**Source:** `src/tools/analysis/empty_folders/empty_folders.py`  
**Constitution §7 requirement:** All key user actions reachable by keyboard; side-effect actions identified for dry-run assessment.

---

## Key Actions

| # | Action Name | Keyboard Path | Has Side Effects? |
|---|---|---|---|
| 1 | Select Root Directory | `Tab` to "Select Directory" button → `Enter`; file dialog opens | No — selection only |
| 2 | Find Empty Folders | `Tab` to "Find Empty Folders" button → `Enter` | No — scans in background worker thread; read-only |
| 3 | Review Found Folders | `Tab` to results list → arrow keys; `Space` to select/deselect items | No — display and selection only |
| 4 | Delete Selected Folders | `Tab` to "Delete Selected" button → `Enter` (requires confirmation) | **Yes** — removes selected empty directories; irreversible |
| 5 | Delete All Found Folders | `Tab` to "Delete All Found" button → `Enter` (requires confirmation) | **Yes** — batch-removes all discovered empty directories; irreversible |
| 6 | Stop Scan | `Tab` to "Stop" button → `Enter` (available during active scan) | No — cancels in-progress scan |

### Notes

- Actions 4 and 5 are **Critical Engine operations** (batch, irreversible). Confirmation dialogs MUST appear before either executes (spec §5.2).
- Action 2 (Find Empty Folders) is the natural dry-run step that MUST precede Actions 4 and 5, satisfying spec §5.2.
