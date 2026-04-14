# KEY_ACTIONS — Security Scanner

**Tool:** Security Scanner  
**Source:** `src/tools/security/security_scanner/security_scanner.py`  
**Constitution §7 requirement:** All key user actions reachable by keyboard; side-effect actions identified for dry-run assessment.

---

## Key Actions

| # | Action Name | Keyboard Path | Has Side Effects? |
|---|---|---|---|
| 1 | Enable System Information Scan | `Tab` to "Scan System Information" checkbox → `Space` to toggle | No — enables scope; no immediate scan |
| 2 | Enable Network Port Scan | `Tab` to "Scan Network Ports" checkbox → `Space` to toggle | No — enables scope; no immediate scan |
| 3 | Enable File Permissions Check | `Tab` to "Check File Permissions" checkbox → `Space` to toggle | No — enables scope; no immediate scan |
| 4 | Enable Running Processes Analysis | `Tab` to "Analyze Running Processes" checkbox → `Space` to toggle | No — enables scope; no immediate scan |
| 5 | Start Security Scan | `Tab` to "Start Security Scan" button → `Enter` | No — gathers information; read-only; background worker thread |
| 6 | View Scan Results | `Tab` to results text area → arrow keys / `Page Up` / `Page Down` | No — reads in-memory results |
| 7 | Monitor Scan Progress | Progress bar updates automatically during scan | No — display only |

### Notes

- All Security Scanner operations are read-only with respect to the filesystem. The tool gathers and reports; it does not modify any system state.
- No side-effect actions; no dry-run requirement.
