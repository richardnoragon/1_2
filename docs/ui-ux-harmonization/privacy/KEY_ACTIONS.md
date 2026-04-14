# KEY_ACTIONS — Privacy

**Tool:** Privacy (Privacy Cleaner / Anonymizer)  
**Source:** `src/tools/privacy/`  
**Constitution §7 requirement:** All key user actions reachable by keyboard; side-effect actions identified for dry-run assessment.

---

## Key Actions

| # | Action Name | Keyboard Path | Has Side Effects? |
|---|---|---|---|
| 1 | Select Privacy Data Target(s) | `Tab` to checklist or tree of privacy targets (browsing history, cache, temp files) → `Space` to select items | No — selection only |
| 2 | Preview / Dry Run | `Tab` to "Preview" or "Scan" button → `Enter` | No — shows items that would be cleaned; no deletions |
| 3 | Clean Privacy Data | `Tab` to "Clean" or "Clean Selected" button → `Enter` (requires confirmation) | **Yes** — deletes selected browsing data, cache, temp files; irreversible |
| 4 | Select Files to Anonymize | `Tab` to "Select Files" button → `Enter`; file dialog opens | No — selection only |
| 5 | Choose Anonymization Level | `Tab` to level selector (Light / Medium / Deep) → arrow keys | No — configuration only |
| 6 | Preview Anonymization | `Tab` to "Preview" button → `Enter` | No — shows what metadata/PII will be removed |
| 7 | Anonymize Files | `Tab` to "Anonymize" button → `Enter` (requires confirmation) | **Yes** — removes PII and metadata from files; irreversible |
| 8 | Enable Secure Deletion | `Tab` to "Secure Delete" checkbox → `Space` | No — changes deletion method for next clean operation |
| 9 | Schedule Automatic Cleaning | `Tab` to "Schedule" options → configure interval → `Tab` to "Save Schedule" → `Enter` | **Yes** — registers a background cleanup task |

### Notes

- Actions 3, 7, and 9 are side-effect operations. Confirmation dialogs MUST appear before each executes (spec §5.2).
- Actions 2 and 6 (Preview) are the natural dry-run steps that MUST precede Actions 3 and 7 respectively (spec §5.2).
- Source path `src/tools/privacy/` may contain subdirectories (`anonymizer/`, `privacy_tools/`); button labels to be confirmed during Phase 3 assessment.
