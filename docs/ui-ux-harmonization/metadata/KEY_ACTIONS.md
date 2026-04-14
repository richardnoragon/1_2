# KEY_ACTIONS — Metadata

**Tool:** Metadata (Image Metadata Editor)  
**Source:** `src/tools/metadata/image_metadata/gui.py`  
**Constitution §7 requirement:** All key user actions reachable by keyboard; side-effect actions identified for dry-run assessment.

---

## Key Actions

| # | Action Name | Keyboard Path | Has Side Effects? |
|---|---|---|---|
| 1 | Select Image File(s) | `Tab` to "Select Files" or "Browse" button → `Enter`; file dialog opens | No — selection only |
| 2 | Load Metadata | `Tab` to "Load Metadata" button → `Enter` (or auto-loads on file selection) | No — reads EXIF/IPTC/XMP from file; no writes |
| 3 | Auto-Detect Metadata Type | `Tab` to "Auto-detect" radio button → `Space` to activate | No — changes active metadata schema view |
| 4 | Edit Metadata Fields | `Tab` to individual metadata form fields → type new values | No — modifies values in memory only; no writes until saved |
| 5 | Save Metadata Changes | `Tab` to "Save Changes" button → `Enter` | **Yes** — writes modified metadata back to image files; modifies original files |
| 6 | Remove All EXIF Data | `Tab` to "Remove EXIF" button → `Enter` (requires confirmation) | **Yes** — strips all EXIF from file(s); irreversible without backup |
| 7 | Batch Edit Metadata | `Tab` to batch batch mode toggle or file list multi-select → apply action | **Yes** — applies metadata changes to multiple files simultaneously |
| 8 | Export Metadata Report | `Tab` to "Export" button → `Enter`; save dialog opens | No — writes metadata report to JSON/CSV; does not modify images |

### Notes

- Actions 5, 6, and 7 are side-effect operations. Confirmation MUST be required for Actions 6 and 7 (spec §5.2).
- Action 4 combined with Action 5 forms the natural preview-then-save flow; there is no separate "dry run" for metadata editing — the edit/preview-before-save UX satisfies spec §5.2.
- Background worker thread used for batch processing; progress signals emit to UI.
