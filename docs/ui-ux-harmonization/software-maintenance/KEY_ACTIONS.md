# KEY_ACTIONS — Software Maintenance

**Tool:** Software Maintenance  
**Source:** `src/tools/system/software_maintenance/software_maintenance.py`  
**Constitution §7 requirement:** All key user actions reachable by keyboard; side-effect actions identified for dry-run assessment.

---

## Key Actions

| # | Action Name | Keyboard Path | Has Side Effects? |
|---|---|---|---|
| 1 | Check for Updates | `Tab` to "Check for Updates" button → `Enter` | No — queries update sources; read-only |
| 2 | Preview Updates | `Tab` to results list → arrow keys | No — displays available updates; no installs |
| 3 | Install Updates | `Tab` to "Install Updates" button → `Enter` (requires confirmation) | **Yes** — modifies system software; may require restart |
| 4 | Uninstall Software | `Tab` to "Uninstall" button → `Enter` (requires confirmation) | **Yes** — removes application files; irreversible |
| 5 | Repair Installation | `Tab` to "Repair" button → `Enter` (requires confirmation) | **Yes** — modifies application files |
| 6 | Refresh List | `Tab` to "Refresh" button → `Enter` | No — re-reads installed software list |

### Notes

- Actions 3, 4, and 5 are side-effect operations. Confirmation dialogs MUST appear before each executes (spec §5.2).
- Action 2 (Preview Updates) is the natural dry-run step that MUST be shown to the user before Actions 3–5 are reachable (spec §5.2).
