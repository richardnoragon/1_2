# KEY_ACTIONS — Secure Delete

**Tool:** Secure Delete  
**Source:** `src/tools/file_operations/secure_delete/secure_delete.py`  
**Constitution §7 requirement:** All key user actions reachable by keyboard; side-effect actions identified for dry-run assessment.

---

## Key Actions

| # | Action Name | Keyboard Path | Has Side Effects? |
|---|---|---|---|
| 1 | Select Files to Delete | `Tab` to "Select Files" button → `Enter`; file dialog opens | No — selection only |
| 2 | Select Folder to Delete | `Tab` to "Select Folder" button → `Enter`; folder dialog opens | No — selection only |
| 3 | Choose Deletion Method | `Tab` to deletion method selector (passes, overwrite algorithm) → arrow keys | No — configuration only; no writes |
| 4 | Preview / Confirm Selection | `Tab` to selected items list; review before deleting | No — displays what will be deleted |
| 5 | Show Help | `Tab` to Help button or menu → `Enter` | No — displays help dialog |
| 6 | Secure Delete (Execute) | `Tab` to "Delete" / "Secure Delete" button → `Enter` (requires confirmation dialog) | **Yes** — multi-pass overwrites and removes target files/folders; **fully irreversible** |
| 7 | Cancel Delete | `Tab` to "Cancel" button → `Enter` (available during active deletion) | No — halts in-progress deletion |

### Notes

- Action 6 (Secure Delete) is a **Critical Engine operation** (irreversible, security-sensitive, multi-file writes). It MUST display a confirmation dialog listing the targets before executing (spec §5.2).
- Steps 1–4 constitute the natural dry-run flow (selection + review before execution), satisfying spec §5.2.
- Button labels confirmed from source: `QPushButton("Select Files")`, `QPushButton("Select Folder")`, `delete_button` connected to `self.secure_delete`.
