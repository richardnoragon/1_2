# KEY_ACTIONS — System Diagnostics

**Tool:** System Diagnostics  
**Source:** `src/tools/system/system_diagnostics/system_diagnostics_gui.py`  
**Constitution §7 requirement:** All key user actions reachable by keyboard; side-effect actions identified for dry-run assessment.

---

## Key Actions

| # | Action Name | Keyboard Path | Has Side Effects? |
|---|---|---|---|
| 1 | Full System Scan | `Tab` to "Full System Scan" button → `Enter` | No — collects OS, hardware, network data; read-only |
| 2 | Quick Health Check | `Tab` to "Quick Health Check" button → `Enter` | No — rapid assessment; read-only |
| 3 | View System Information | `Tab` to "System Information" tab → browse sub-tabs | No — displays OS, CPU, memory info |
| 4 | View Performance Metrics | `Tab` to "Performance" tab | No — displays real-time CPU/RAM usage |
| 5 | View Hardware Details | `Tab` to "Hardware" tab | No — displays storage, GPU, peripherals |
| 6 | View Network Status | `Tab` to "Network" tab | No — displays network interfaces and connectivity |
| 7 | View Health Check Results | `Tab` to "Health Check" tab | No — displays health pass/fail summary |
| 8 | Export Report | `Tab` to "Export Report" button → `Enter`; save dialog opens | No — writes diagnostics to file at chosen path |

### Notes

- All System Diagnostics operations are read-only; no side effects.
- Tabs accessible by `Tab` + `Space` / arrow keys in standard Qt tab navigation.
