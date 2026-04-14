# KEY_ACTIONS — Simple System Info

**Tool:** Simple System Info  
**Source:** `src/tools/system/simple_system_info.py`  
**Constitution §7 requirement:** All key user actions reachable by keyboard; side-effect actions identified for dry-run assessment.

---

## Key Actions

| # | Action Name | Keyboard Path | Has Side Effects? |
|---|---|---|---|
| 1 | Refresh System Information | `Tab` to "Refresh" button → `Enter` (or auto-populated on open) | No — re-reads OS/hardware data; read-only |
| 2 | View CPU Information | `Tab` to CPU section / panel | No — displays processor model, speed, cores |
| 3 | View Memory Information | `Tab` to Memory section / panel | No — displays total/used/available RAM |
| 4 | View OS Information | `Tab` to OS section / panel | No — displays OS version, build, uptime |

### Notes

- All Simple System Info operations are read-only; no side effects.
- This is a lightweight display tool; actions consist primarily of viewing pre-populated panels.
