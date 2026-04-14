# KEY_ACTIONS — Duplicate Finder

**Tool:** Duplicate Finder  
**Source:** `src/tools/analysis/duplicate_finder/find_duplicate_files.py`  
**Constitution §7 requirement:** All key user actions reachable by keyboard; side-effect actions identified for dry-run assessment.

---

## Key Actions

| # | Action Name | Keyboard Path | Has Side Effects? |
|---|---|---|---|
| 1 | Select Directory | `Tab` to "Select Directory" button → `Enter`; file dialog opens | No — selection only |
| 2 | Find Duplicates | `Tab` to "Find Duplicates" button → `Enter`; `F5` | No — MD5 scan runs in background thread; read-only |
| 3 | Review Results | `Tab` to results list → arrow keys to navigate; `Space` to select/deselect individual items | No — display and selection only |
| 4 | Export Results | `Tab` to "Export" button or menu item → `Enter` | No — writes findings to CSV/JSON; does not modify source files |
| 5 | Delete Selected Duplicates | `Tab` to "Delete Selected" button → `Enter` (requires confirmation dialog) | **Yes** — deletes selected duplicate files; irreversible |
| 6 | New Scan / Clear | `F5` or `Tab` to "New Scan" button → `Enter` | No — clears current results and resets form |
| 7 | Exit | `Ctrl+Q` | No |

### Notes

- Action 5 (Delete Selected Duplicates) is a **Critical Engine operation** (batch, irreversible). A confirmation dialog MUST appear before deletion proceeds (spec §5.2).
- Steps 1–4 constitute the natural dry-run flow (scan + review before delete), satisfying spec §5.2 dry-run requirement.
- `F5` shortcut found in source (`new_scan` / `refresh` action).
