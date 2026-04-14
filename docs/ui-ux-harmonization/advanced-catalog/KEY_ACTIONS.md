# KEY_ACTIONS — Advanced Catalog

**Tool:** Advanced Catalog  
**Source:** `src/tools/file_management/advanced_catalog/advanced_catalog_window.py`  
**Constitution §7 requirement:** All key user actions reachable by keyboard; side-effect actions identified for dry-run assessment.

---

## Key Actions

| # | Action Name | Keyboard Path | Has Side Effects? |
|---|---|---|---|
| 1 | Select Directory to Scan | `Tab` to "Select Directory" button → `Enter`; file dialog opens | No — selection only |
| 2 | Scan Directory | `Tab` to "Scan" button → `Enter`; runs `FileScanThread` in background | No — traverses and reads file system; no writes |
| 3 | Select Sort Criteria | `Tab` to sort `QComboBox` → arrow keys to change option | No — re-orders in-memory results |
| 4 | Select Color Scheme | `Tab` to color scheme `QComboBox` → arrow keys to change option | No — changes display visual only |
| 5 | Export Catalog | `Tab` to "Export" button → `Enter`; runs `ExportThread`; save dialog opens | No — writes catalog to HTML/CSV/JSON at chosen path |
| 6 | Generate Report | `Tab` to "Generate Report" button → `Enter` | No — creates analysis report; read-only |

### Notes

- All Advanced Catalog operations are read-only with respect to the scanned file system.
- Export (Action 5) writes an output file but does not modify source data.
