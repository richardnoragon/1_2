# KEY_ACTIONS — Preferences

**Tool:** Preferences  
**Source:** `src/tools/preferences/portability_launcher.py`  
**Constitution §7 requirement:** All key user actions reachable by keyboard; side-effect actions identified for dry-run assessment.

---

## Key Actions

| # | Action Name | Keyboard Path | Has Side Effects? |
|---|---|---|---|
| 1 | Open Preferences | Launched from Hub menu or tool list | No — opens preferences interface |
| 2 | Change Setting | `Tab` to specific setting control → `Space` (checkbox) / arrow keys (dropdown) / type (text field) | No — modifies value in memory only until saved |
| 3 | Save Settings | `Tab` to "Save" or "Apply" button → `Enter` | **Yes** — persists configuration changes to `config/rfu_config.json`; overwrites current settings |
| 4 | Reset to Defaults | `Tab` to "Reset to Default" button → `Enter` (requires confirmation) | **Yes** — restores all settings to factory defaults; overwrites current configuration |
| 5 | Import Settings | `Tab` to "Import" button → `Enter`; file dialog opens | **Yes** — loads settings from file; overwrites current configuration |
| 6 | Export Settings | `Tab` to "Export" button → `Enter`; save dialog opens | No — writes current config to a new file; does not modify active settings |
| 7 | Cancel / Discard Changes | `Tab` to "Cancel" button → `Enter` (or close window) | No — discards unsaved in-memory changes |

### Notes

- Actions 3, 4, and 5 are side-effect operations. Actions 4 and 5 MUST have confirmation dialogs (spec §5.2).
- Action 2 combined with Action 7 provides a natural "preview before commit" flow.
