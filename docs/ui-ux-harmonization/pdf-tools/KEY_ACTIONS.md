# KEY_ACTIONS — PDF Tools

**Tool:** PDF Tools (Batch Processor + Functional Integration)  
**Source:** `src/tools/pdf_tools/batch_processor.py`, `src/tools/pdf_tools/pdf_functional_integration.py`  
**Constitution §7 requirement:** All key user actions reachable by keyboard; side-effect actions identified for dry-run assessment.

---

## Key Actions

| # | Action Name | Keyboard Path | Has Side Effects? |
|---|---|---|---|
| 1 | Select PDF File(s) | `Tab` to "Select Files" or file browser → `Enter`; file dialog opens | No — selection only |
| 2 | **Merge PDFs** | `Tab` to "Basic Operations" tab → `Tab` to "Merge PDFs" button → `Enter` | **Yes** — creates a combined PDF file |
| 3 | **Split PDF** | `Tab` to "Basic Operations" tab → `Tab` to "Split PDF" button → `Enter` | **Yes** — creates multiple output PDF files |
| 4 | **Rotate Pages** | `Tab` to "Basic Operations" tab → configure rotation → `Tab` to "Rotate" button → `Enter` | **Yes** — modifies page orientation in output PDF |
| 5 | **Delete Pages** | `Tab` to "Basic Operations" tab → select pages → `Tab` to "Delete Pages" button → `Enter` (requires confirmation) | **Yes** — removes pages; irreversible in output |
| 6 | Convert to Image | `Tab` to "Conversion" tab → `Tab` to "To Image" button → `Enter` | No — exports pages as image files; does not modify source PDF |
| 7 | Convert to Text | `Tab` to "Conversion" tab → `Tab` to "To Text" button → `Enter` | No — extracts text to file; does not modify source PDF |
| 8 | Convert from Image to PDF | `Tab` to "Conversion" tab → `Tab` to "From Image" button → `Enter` | **Yes** — creates a new PDF from image files |
| 9 | Extract Text | `Tab` to "Content Extraction" tab → `Tab` to "Extract Text" button → `Enter` | No — reads and exports text content |
| 10 | Extract Images | `Tab` to "Content Extraction" tab → `Tab` to "Extract Images" button → `Enter` | No — reads and saves embedded images |
| 11 | Extract Tables | `Tab` to "Content Extraction" tab → `Tab` to "Extract Tables" button → `Enter` | No — reads and exports table data |
| 12 | Add Password / Encrypt PDF | `Tab` to "Security" tab → enter password → `Tab` to "Add Password" button → `Enter` | **Yes** — encrypts PDF; modifies output file |
| 13 | Remove Password / Decrypt PDF | `Tab` to "Security" tab → enter password → `Tab` to "Remove Password" button → `Enter` | **Yes** — removes encryption; modifies output file |
| 14 | Redact Content | `Tab` to "Security" tab → select regions → `Tab` to "Redact" button → `Enter` (requires confirmation) | **Yes** — permanently obscures selected text/images; **irreversible** |
| 15 | Analyze PDF Structure | `Tab` to "Analysis" tab → `Tab` to "Analyze" button → `Enter` | No — reads PDF structure; no writes |
| 16 | View PDF Metrics | `Tab` to "Analysis" tab → metrics panel | No — displays file size, page dimensions, etc. |
| 17 | Batch Process | `Tab` to batch file list → multi-select → configure operation → `Tab` to "Run Batch" button → `Enter` | **Yes** — applies operations to multiple PDFs; side effects depend on selected operation |
| 18 | Monitor Batch Progress | Progress bar updates automatically | No — display only |
| 19 | Cancel Batch | `Tab` to "Cancel" button → `Enter` (during active batch) | No — halts in-progress batch |

### Notes

- Actions 2–5, 8, 12–14, and 17 are side-effect operations. Actions 5, 14, and 17 MUST have confirmation dialogs (spec §5.2).
- Action 14 (Redact) is fully irreversible. It MUST require confirmation and SHOULD offer a preview before execution.
- Batch Processor (Action 17) is a **Critical Engine operation** (batch, multi-file writes).
- Dry-run requirement for Actions 2–5: Analysis (Action 15) and structure view satisfy the "preview before primary action" requirement for the Basic Operations tab.
