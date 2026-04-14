# KEY_ACTIONS — Organizer

**Tool:** Organizer  
**Source:** `src/tools/file_management/organizer/organize.py`  
**Constitution §7 requirement:** All key user actions reachable by keyboard; side-effect actions identified for dry-run assessment.

---

## Key Actions

| # | Action Name | Keyboard Path | Has Side Effects? |
|---|---|---|---|
| 1 | Select Directory to Organize | `Tab` to directory selector button → `Enter`; file dialog opens | No — selection only |
| 2 | Load Organization Rules | `Tab` to "Load Settings" menu item → `Enter` (auto-loaded on init as well) | No — reads rules from file; no writes |
| 3 | Preview / Dry Run | `Tab` to "Preview" or "Dry Run" button → `Enter` | No — simulates organization; shows what would move/rename |
| 4 | Run Organization | `Tab` to "Organize" / primary action button → `Enter` (requires dry-run first) | **Yes** — moves/renames files according to rules; irreversible without manual revert |
| 5 | Save Organization Settings | Menu: "Save Settings" → `Enter` | **Yes** — persists current rules to configuration file |
| 6 | Load Organization Settings | Menu: "Load Settings" → `Enter` | No — reads settings; no writes to file system data |
| 7 | Export Results | Menu: "Export Results" → `Enter` | No — writes operation log to a chosen file |
| 8 | Clear / Reset | Menu: "Clear" → `Enter` | **Yes** — resets the current rule set; previously saved settings unaffected |

### Notes

- Action 4 (Run Organization) is a **Critical Engine operation** (multi-file writes, potentially irreversible without backup). A dry-run control (Action 3) MUST be present and reachable before the primary action is available (spec §5.2).
