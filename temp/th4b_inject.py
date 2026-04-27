"""
TH-4b injection script: adds ThemeManager callback registration to all rows 4-25 tool files.
For each file:
  1. Adds ThemeManager to the `from src.gui.themes import token` line (or adds a new import)
  2. Injects `ThemeManager.add_theme_changed_callback(self._on_theme_changed)` near end of
     the primary GUI class __init__
  3. Adds `_on_theme_changed(self, variant: str) -> None:` method after __init__

Run from the workspace root: python temp/th4b_inject.py
"""

import pathlib
import re
import sys

FILES = {
    "duplicate_finder": "src/tools/analysis/duplicate_finder/find_duplicate_files.py",
    "checksum": "src/tools/analysis/checksum/check_sum.py",
    "size_analyzer": "src/tools/analysis/size_analyzer/size_analyzer.py",
    "empty_folders": "src/tools/analysis/empty_folders/empty_folders.py",
    "finder": "src/tools/file_management/finder/file_finder.py",
    "organizer": "src/tools/file_management/organizer/organize.py",
    "advanced_catalog": "src/tools/file_management/advanced_catalog/catalog_tool.py",
    "system_diagnostics": "src/tools/system/diagnostics_monitoring/system_diagnostics_gui.py",
    "process_monitor": "src/tools/system/process_monitor/process_monitor.py",
    "simple_system_info": "src/tools/system/simple_system_info.py",
    "software_maintenance": "src/tools/system/software_maintenance/gui/maintenance_hub.py",
    "network": "src/tools/network/network_connectivity_complex/gui/hub.py",
    "metadata": "src/tools/metadata/office_metadata/office_metadata_gui.py",
    "secure_delete": "src/tools/file_operations/secure_delete/secure_delete.py",
    "encryption": "src/tools/security/encryption/en_and_decrypt.py",
    "security_scanner": "src/tools/security/security_scanner/security_scanner.py",
    "password_generator": "src/tools/security/password_generator/password_generator.py",
    "pdf_tools": "src/tools/pdf_tools/widgets/enhanced_pdf_tools_widget.py",
    "privacy": "src/tools/privacy/privacy_tools/gui/privacy_hub.py",
    # Rows 16 and 19 live in tabbed_hub
    "logs_and_file_ops": "src/tabbed_hub.py",
}

# Methods to call in _on_theme_changed if they exist in the file
APPLY_METHODS = [
    "_apply_theme",
    "_apply_styles",
    "setup_styles",
    "_setup_styles",
    "_apply_stylesheet",
    "_update_styles",
]

CALLBACK_LINE = (
    "        ThemeManager.add_theme_changed_callback(self._on_theme_changed)\n"
)

THEME_METHOD_TEMPLATE = (
    "\n"
    "    def _on_theme_changed(self, variant: str) -> None:\n"
    '        """Re-apply token-based stylesheets when the active theme variant changes."""\n'
    "        {body}\n"
)


def get_apply_call(txt: str) -> str:
    for m in APPLY_METHODS:
        if re.search(rf"def {re.escape(m)}\b", txt):
            return f"self.{m}()"
    return "pass  # stylesheets applied at init; live re-apply pending TH-4c/4d"


def add_theme_manager_import(txt: str) -> tuple[str, str]:
    """Add ThemeManager to import; return (new_txt, note)."""
    # Already present?
    if "ThemeManager" in txt:
        return txt, "ThemeManager already imported"
    # Try to extend existing 'from src.gui.themes import token'
    new_txt = re.sub(
        r"(from src\.gui\.themes import\s+)(token)\b",
        r"\1ThemeManager, \2",
        txt,
        count=1,
    )
    if new_txt != txt:
        return new_txt, "Added ThemeManager to existing themes import"
    # No themes import at all — add one after PyQt5 imports block
    # Find last PyQt5 import line
    lines = txt.splitlines(keepends=True)
    insert_after = -1
    for i, line in enumerate(lines):
        if line.startswith("from PyQt5") or line.startswith("import PyQt5"):
            insert_after = i
    if insert_after >= 0:
        lines.insert(
            insert_after + 1, "from src.gui.themes import ThemeManager, token\n"
        )
        return "".join(lines), "Added new themes import after PyQt5 imports"
    # Fallback: insert at top after existing imports
    lines.insert(0, "from src.gui.themes import ThemeManager, token\n")
    return "".join(lines), "Added themes import at top (fallback)"


def find_primary_class_init(txt: str) -> tuple[str, int] | None:
    """
    Returns (class_name, line_index_of_first_def_after_init) for the primary GUI class.
    Primary = largest QMainWindow/QWidget/StandardWindow subclass __init__.
    """
    lines = txt.splitlines()
    # Find all class definitions and rank by number of method lines until next class
    classes = []
    for i, line in enumerate(lines):
        m = re.match(r"^class (\w+)\(", line)
        if m:
            classes.append((i, m.group(1)))

    best = None
    best_score = -1
    for ci, (class_line_idx, class_name) in enumerate(classes):
        # Find __init__ within this class
        init_idx = None
        end_of_class = classes[ci + 1][0] if ci + 1 < len(classes) else len(lines)
        for j in range(class_line_idx, end_of_class):
            if re.match(r"    def __init__\b", lines[j]):
                init_idx = j
                break
        if init_idx is None:
            continue
        # Score = lines in __init__
        next_def = None
        for j in range(init_idx + 1, end_of_class):
            stripped = lines[j].strip()
            if stripped and not stripped.startswith("#"):
                indent = len(lines[j]) - len(lines[j].lstrip())
                if indent == 4 and stripped.startswith("def "):
                    next_def = j
                    break
        score = (next_def or end_of_class) - init_idx
        if score > best_score:
            best_score = score
            best = (class_name, init_idx, next_def, end_of_class)

    return best


def inject_callback_in_init(
    lines: list[str], init_idx: int, next_def_idx: int | None
) -> tuple[list[str], str]:
    """Insert callback call as the last non-trivial statement before end of __init__."""
    end = next_def_idx if next_def_idx else len(lines)
    # Find the last non-empty, non-comment line within __init__ body (indent > 4)
    insert_at = end  # default: before next def
    for j in range(end - 1, init_idx, -1):
        stripped = lines[j].strip()
        if stripped and not stripped.startswith("#"):
            indent = len(lines[j]) - len(lines[j].lstrip())
            if indent >= 8:  # inside __init__ body
                insert_at = j + 1
                break

    # Don't insert before a self.show() call if it's the last line
    for j in range(insert_at - 1, init_idx, -1):
        stripped = lines[j].strip()
        if stripped and not stripped.startswith("#"):
            if stripped.startswith("self.show()") or stripped.startswith("self.show("):
                insert_at = j  # insert before show()
            break

    lines.insert(insert_at, CALLBACK_LINE)
    return lines, f"Callback inserted at line {insert_at}"


def inject_theme_method(
    lines: list[str], next_def_idx: int | None, end_of_class: int, apply_call: str
) -> list[str]:
    """Insert _on_theme_changed method after __init__."""
    insert_at = next_def_idx if next_def_idx else end_of_class
    # Adjust for the callback line we already inserted
    method_txt = THEME_METHOD_TEMPLATE.format(body=apply_call)
    method_lines = method_txt.splitlines(keepends=True)
    for i, ml in enumerate(method_lines):
        lines.insert(insert_at + i, ml)
    return lines


def process_file(tool: str, fpath: str) -> str:
    p = pathlib.Path(fpath)
    if not p.exists():
        return f"  SKIP: file not found"

    txt = p.read_text(encoding="utf-8", errors="ignore")

    # Skip if already done
    if "add_theme_changed_callback" in txt:
        return f"  SKIP: callback already registered"

    # 1. Add ThemeManager import
    txt, import_note = add_theme_manager_import(txt)

    # 2. Find primary class __init__
    result = find_primary_class_init(txt)
    if result is None:
        return f"  SKIP: no class with __init__ found"

    class_name, init_idx, next_def_idx, end_of_class = result
    apply_call = get_apply_call(txt)

    # 3. Inject callback call
    lines = txt.splitlines(keepends=True)
    lines, cb_note = inject_callback_in_init(lines, init_idx, next_def_idx)

    # Adjust indices for the inserted line
    if next_def_idx is not None:
        next_def_idx += 1
    end_of_class += 1

    # 4. Inject _on_theme_changed method
    lines = inject_theme_method(lines, next_def_idx, end_of_class, apply_call)

    new_txt = "".join(lines)
    p.write_text(new_txt, encoding="utf-8")
    return f"  OK: {import_note}; {cb_note}; class={class_name}; apply={apply_call}"


def main():
    results = []
    for tool, fpath in FILES.items():
        msg = process_file(tool, fpath)
        results.append((tool, fpath, msg))
        print(f"{tool}: {msg}")
    ok = sum(1 for _, _, m in results if m.strip().startswith("OK"))
    skip = sum(1 for _, _, m in results if m.strip().startswith("SKIP"))
    print(f"\nDone: {ok} modified, {skip} skipped")


if __name__ == "__main__":
    main()
