# KEY_ACTIONS — Finder (File Finder)

**Tool:** Finder / File Finder  
**Source:** `src/tools/file_management/finder/file_finder.py`  
**Constitution §7 requirement:** All key user actions reachable by keyboard; side-effect actions identified for dry-run assessment.

---

## Key Actions

| # | Action Name | Keyboard Path | Has Side Effects? |
|---|---|---|---|
| 1 | Select Search Directory | `Tab` to "Select Directory" button (`select_pushButton`) → `Enter`; file dialog opens | No — selection only |
| 2 | Set Search Criteria | `Tab` to search filter fields (extension, name pattern, date range) → type values | No — configuration only |
| 3 | Execute Search | `Tab` to "Search" button (`search_pushButton`) → `Enter` | No — file system traversal; read-only |
| 4 | View File Metadata | Click or `Tab` to results `listView` → arrow keys to navigate; metadata table auto-populates | No — reads file properties; no writes |
| 5 | Open File | Double-click in results list or context menu → `Enter` | Possible — opens file with system default application; the file itself may be modified by the opening app |
| 6 | Exit | `Ctrl+Q` | No |

### Notes

- All Finder operations are read-only from the tool's perspective.
- Action 5 (Open File) is classified "Possible" because the source application's default opener may modify the file (e.g. Word updating last-opened timestamp).
- `Ctrl+Q` shortcut confirmed in source.
