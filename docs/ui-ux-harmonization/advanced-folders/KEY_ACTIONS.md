# KEY_ACTIONS — Advanced Folders

**Tool:** Advanced Folders  
**Source:** `src/tools/file_management/advanced_folders/`  
**Constitution §7 requirement:** All key user actions reachable by keyboard; side-effect actions identified for dry-run assessment.

---

## Key Actions

| # | Action Name | Keyboard Path | Has Side Effects? |
|---|---|---|---|
| 1 | New Folder | `Tab` to "New Folder" button → `Enter` | **Yes** — creates a new folder configuration entry; persists to settings |
| 2 | Edit Folder | `Tab` to "Edit" button → `Enter` (enabled only when a folder is selected in list) | **Yes** — modifies the selected folder's configuration |
| 3 | Delete Folder | `Tab` to "Delete" button → `Enter` (enabled only when a folder is selected) | **Yes** — removes folder configuration entry; irreversible |
| 4 | Refresh | `Tab` to "Refresh" button → `Enter` (enabled after folder selected) | No — re-scans the selected folder; read-only |
| 5 | Search | `Tab` to "Search" button → `Enter` (enabled after folder selected); or type in Quick Search field + `Return` | No — executes a filtered query; read-only |
| 6 | Settings | `Tab` to "⚙️ Settings" button → `Enter` | No — opens configuration dialog; no immediate file writes |
| 7 | Export Results | `Tab` to "📤 Export" button → `Enter` (enabled when results are present) | No — writes a CSV/JSON file to a chosen export path |

### Notes

- Actions 1–3 affect folder configuration (stored in `config/` JSON), not file system contents directly.
- Action 7 (Export) writes an output file; it is classified as No side effect because it does not modify existing data.
- No global keyboard shortcuts were found in source; all actions are Tab-reachable.
