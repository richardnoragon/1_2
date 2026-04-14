"""Fix FN-028 row in TASKS.md — write using script file to avoid shell escaping."""

fn028 = (
    "| FN-028 | April 2026 | A11Y-8c | "
    "Compact mini-toolbar buttons in `folder_tree_view.py` (line ~730) and "
    "`search_results_table.py` (line ~801) are constrained to 28\u00d728 px by "
    "`toolbar_frame.setMaximumHeight(32)` with 4 px top/bottom margins, below the "
    "44\u00d744 px WCAG 2.1 SC 2.5.8 minimum touch-target size. "
    "**Design rationale:** These mini toolbars are compact panel-chrome rows embedded "
    "at the top of tree/results panels; doubling their height to meet 44 px would "
    "inflate the panel chrome by ~37%, disrupting the two-panel split-view layout. "
    "Each action has a keyboard/menu alternative: \u201cNew Folder\u201d and \u201cRefresh\u201d via "
    "right-click context menu; \u201cExport\u201d, \u201cCopy\u201d, \u201cSelect All\u201d via menu bar entries "
    "and keyboard shortcuts. "
    "**Accepted deviation:** Compact panel-chrome constraint with full keyboard "
    "alternatives satisfies the spirit of spec \u00a74.3; the 44 px requirement is "
    "mandatory for standalone toolbar buttons (fulfilled via `setMinimumSize(44, 44)` "
    "in `_create_toolbar_button()` for the main toolbar). "
    "**Constraint:** If either mini toolbar is ever redesigned as a standalone or "
    "floating toolbar, the 44\u00d744 px minimum MUST be applied at that time. |\n"
)

tasks_path = r"c:\Users\HP1\1_2\docs\ui-ux-harmonization\TASKS.md"
with open(tasks_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find current line 43 (0-indexed: 42) — should be the mangled FN-028 we just wrote
# Replace line 42 with the correct FN-028
if lines[42].startswith("| FN-028"):
    # Already replaced duplicates, just fix the mangled content
    lines[42] = fn028
    print("Fixed mangled FN-028 row.")
elif lines[42].startswith("| FN-026"):
    # Duplicates still present — remove them and insert FN-028
    lines[42:44] = [fn028]
    print("Replaced duplicate rows with FN-028.")
else:
    print(f"Unexpected content at line 43: {repr(lines[42][:60])}")
    raise SystemExit(1)

with open(tasks_path, "w", encoding="utf-8") as f:
    f.writelines(lines)

with open(tasks_path, "r", encoding="utf-8") as f:
    check_lines = f.readlines()
print(f"Line 41: {check_lines[40][:60]}")
print(f"Line 42: {check_lines[41][:60]}")
print(f"Line 43: {check_lines[42][:60]}")
print(f"Line 44: {check_lines[43][:60]}")
