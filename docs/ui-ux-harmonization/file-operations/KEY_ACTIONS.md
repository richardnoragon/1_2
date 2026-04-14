# KEY_ACTIONS — File Operations

**Tool:** File Operations (Copy / Move / Rename / Split / Compress)  
**Source:** `src/tools/file_operations/` (catalog.py, file_finder.py, organize.py, rename/, compression/, file_splitter/, enhanced_editor/)  
**Constitution §7 requirement:** All key user actions reachable by keyboard; side-effect actions identified for dry-run assessment.

---

## Key Actions

| # | Action Name | Keyboard Path | Has Side Effects? |
|---|---|---|---|
| 1 | Select Source File(s) / Directory | `Tab` to "Select Files" or "Select Directory" button → `Enter`; file dialog opens | No — selection only |
| 2 | Select Destination | `Tab` to "Select Destination" button → `Enter`; file dialog opens | No — selection only |
| 3 | Preview / Dry Run | `Tab` to "Preview" or "Dry Run" button → `Enter` | No — simulates operation; shows what will be created/moved/renamed |
| 4 | Copy Files | `Tab` to "Copy" button → `Enter` | **Yes** — creates copies at destination; may overwrite existing files if names clash |
| 5 | Move Files | `Tab` to "Move" button → `Enter` (requires confirmation) | **Yes** — removes source and writes to destination; partially irreversible |
| 6 | Rename Files | `Tab` to "Rename" button → `Enter`; rename editor opens | **Yes** — renames files in-place; irreversible without preview |
| 7 | Split File | `Tab` to "Split" tab → configure chunk size → `Tab` to "Split" button → `Enter` | **Yes** — creates multiple part files; does not delete source |
| 8 | Compress / Archive | `Tab` to "Compress" tab → configure format → `Tab` to "Create Archive" button → `Enter` | No — creates archive; does not modify source files |
| 9 | Cancel Operation | `Tab` to "Cancel" button → `Enter` (available during active operation) | No — halts in-progress operation |
| 10 | Exit | `Ctrl+Q` | No |

### Notes

- Actions 4–7 are side-effect operations. Actions 5 and 6 MUST have confirmation dialogs (spec §5.2).
- Action 3 (Preview / Dry Run) MUST be a visible, reachable control before Actions 4–7 are available (spec §5.2).
- This tool is a **Critical Engine candidate** (multi-file writes, batch operations, partially irreversible).
