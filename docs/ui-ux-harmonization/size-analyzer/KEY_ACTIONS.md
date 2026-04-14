# KEY_ACTIONS — Size Analyzer

**Tool:** Size Analyzer  
**Source:** `src/tools/analysis/size_analyzer/size_analyzer.py`  
**Constitution §7 requirement:** All key user actions reachable by keyboard; side-effect actions identified for dry-run assessment.

---

## Key Actions

| # | Action Name | Keyboard Path | Has Side Effects? |
|---|---|---|---|
| 1 | Select Directory | `Tab` to "Select Directory" button → `Enter`; file dialog opens | No — selection only |
| 2 | Start Analysis / New Scan | `Tab` to "New Scan" or "Start" button → `Enter`; `F5` | No — directory traversal in background thread; read-only |
| 3 | View Results | Analysis populates results table automatically; `Tab` to table → arrow keys | No — display only |
| 4 | Sort Results | `Tab` to column header or sort dropdown → `Enter` / arrow keys | No — re-orders in-memory results |
| 5 | Export Data | `Tab` to "Export" button or menu → `Enter` | No — writes analysis to file at chosen path |
| 6 | Refresh | `F5` | No — re-runs analysis on same directory |
| 7 | Show Help | `F1` | No |
| 8 | Exit | `Ctrl+Q` | No |

### Notes

- All Size Analyzer operations are read-only; no files are modified.
- `Ctrl+Q`, `F1`, and `F5` shortcuts confirmed in source.
