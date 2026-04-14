# KEY_ACTIONS — Process Monitor

**Tool:** Process Monitor  
**Source:** `src/tools/system/process_monitor/process_monitor.py`  
**Constitution §7 requirement:** All key user actions reachable by keyboard; side-effect actions identified for dry-run assessment.

---

## Key Actions

| # | Action Name | Keyboard Path | Has Side Effects? |
|---|---|---|---|
| 1 | Start Auto Refresh | `Tab` to "▶ Auto Refresh" button → `Enter` (toggles to active state) | No — enables periodic UI updates every 3 s; read-only |
| 2 | Stop Auto Refresh | `Tab` to "⏹ Stop Auto" button → `Enter` (visible when auto-refresh is active) | No — disables timer; no writes |
| 3 | Sort by CPU Usage | `Tab` to column header or sort control → `Enter` | No — re-orders visible list |
| 4 | Sort by Memory Usage | `Tab` to column header or sort control → `Enter` | No — re-orders visible list |
| 5 | Sort by Name / PID | `Tab` to column header or sort control → `Enter` | No — re-orders visible list |
| 6 | Kill Process | Context menu on selected process → "Kill Process" → `Enter`; confirmation dialog required | **Yes** — terminates the selected OS process; irreversible for the process state |

### Notes

- Action 6 (Kill Process) is a side-effect action. A confirmation dialog MUST appear before the kill signal is sent (spec §5.2).
- Auto-refresh interval is 3 seconds (hardcoded in source).
