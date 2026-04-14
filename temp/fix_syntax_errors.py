#!/usr/bin/env python3
"""Fix all misplaced 'from src.gui.themes import token/Typography' lines
that were placed inside an open parenthesis group (inside a multi-line import).

Pattern A: inside 'from PyQt5.Xxx import (\n' group
Pattern B: after 'try:\n    from PyQt5.Xxx import' but at column 0 (not indented)
Pattern C: special cases (see individual file comments)
"""
import re
import ast
from pathlib import Path

ROOT = Path("C:/Users/HP1/1_2/src")

def try_parse(path: Path) -> bool:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
        return True
    except SyntaxError:
        return False

def fix_token_inside_open_paren(path: Path, import_line: str) -> bool:
    """Remove 'import_line' from inside an open paren group and place it
    after the closing ')' line, still inside the surrounding try: block."""
    text = path.read_text(encoding="utf-8")
    if import_line not in text:
        return False
    # The import line appears at column 0 or with 0 indent inside a paren:
    # We simply remove it from where it is, and add it as the FIRST line
    # inside the try: block (before the first 'from PyQt5' line).
    # Strategy: remove the bad line, then insert it right after 'try:\n'
    bad_line = import_line + "\n"
    if bad_line not in text:
        return False
    
    # Remove the misplaced line
    new_text = text.replace(bad_line, "", 1)
    
    # Now insert it as first indented line inside the nearest try: block
    # Find the try: block that contains the PyQt5 import
    # We insert it right after 'try:\n' followed by 4-space indent
    # Find position where to insert: after 'try:\n    from PyQt5'
    m = re.search(r'(try:\n)(\s+from PyQt5)', new_text)
    if not m:
        # try: followed by    from PyQt5.QtCore or similar
        m = re.search(r'(try:\n)(\s+from PyQt5)', new_text)
    if m:
        # Determine the indent level from the existing line
        indent = re.match(r'\s+', m.group(2)).group(0)
        insert_pos = m.end(1)  # After 'try:\n'
        new_text = new_text[:insert_pos] + indent + import_line + "\n" + new_text[insert_pos:]
        path.write_text(new_text, encoding="utf-8")
        return try_parse(path)
    
    # Fallback: write anyway (already removed the bad line)
    path.write_text(new_text, encoding="utf-8")
    return try_parse(path)

results = []

# Files where token import is misplaced inside open paren group or after try:
simple_fixes = [
    ("rfu/login_dialog.py", "from src.gui.themes import token"),
    ("tools/preferences/portability_launcher.py", "from src.gui.themes import token"),
    ("tools/security/security_preferences.py", "from src.gui.themes import token"),
    ("tools/system/simple_system_info.py", "from src.gui.themes import token, Typography"),
    ("tools/analysis/size_analyzer/size_analyzer.py", "from src.gui.themes import token"),
    ("tools/file_management/advanced_catalog/advanced_catalog_window.py", "from src.gui.themes import token, Typography"),
    ("tools/file_management/advanced_catalog/catalog_tool.py", "from src.gui.themes import token"),
    ("tools/file_management/advanced_folders/gui/folder_tree_view.py", "from src.gui.themes import token"),
    ("tools/file_management/advanced_folders/gui/preview_pane.py", "from src.gui.themes import token"),
    ("tools/file_management/advanced_folders/gui/search_results_table.py", "from src.gui.themes import token"),
    ("tools/file_operations/rename/rename.py", "from src.gui.themes import token"),
    ("tools/file_operations/secure_delete/secure_delete.py", "from src.gui.themes import token"),
    ("tools/metadata/image_metadata/gui.py", "from src.gui.themes import token"),
    ("tools/metadata/office_metadata/office_metadata_gui.py", "from src.gui.themes import token"),
    ("tools/metadata/office_metadata/office_meta_data_editor.py", "from src.gui.themes import token"),
    ("tools/network/bookmarks/bookmark_manager_gui.py", "from src.gui.themes import token"),
    ("tools/network/connectivity/network_connectivity.py", "from src.gui.themes import token"),
    ("tools/network/scanner/network_scanner.py", "from src.gui.themes import token"),
    ("tools/network/transfer/network_transfer.py", "from src.gui.themes import token"),
    ("tools/pdf_tools/dialogs/extraction_parameter_dialogs.py", "from src.gui.themes import token"),
    ("tools/privacy/privacy_cleaner/privacy_cleaner.py", "from src.gui.themes import token"),
    ("tools/security/password_generator/password_generator.py", "from src.gui.themes import token"),
    ("tools/system/enhanced_clipboard/enhanced_clipboard_gui.py", "from src.gui.themes import token"),
    ("tools/system/permissions/permissions_editor.py", "from src.gui.themes import token"),
    ("tools/system/system_diagnostics/system_diagnostics_gui.py", "from src.gui.themes import token"),
    ("tools/system/diagnostics_monitoring/gui/performance_widget.py", "from src.gui.themes import token, Typography"),
    ("tools/system/software_maintenance/gui/maintenance_hub.py", "from src.gui.themes import token"),
]

for rel, import_line in simple_fixes:
    path = ROOT / rel
    if not path.exists():
        results.append(f"MISSING: {rel}")
        continue
    if try_parse(path):
        results.append(f"ALREADY_OK: {rel}")
        continue
    ok = fix_token_inside_open_paren(path, import_line)
    results.append(f"{'FIXED' if ok else 'FAILED'}: {rel}")

# Special: advanced_catalog_window.py has NO try: block - top-level import group
p = ROOT / "tools/file_management/advanced_catalog/advanced_catalog_window.py"
if not try_parse(p):
    text = p.read_text(encoding="utf-8")
    # The bad line is between 'from PyQt5.QtWidgets import (\n' and its contents
    bad = "from src.gui.themes import token, Typography\n"
    if bad in text:
        text = text.replace(bad, "", 1)
        # Insert before 'from PyQt5.QtWidgets import ('
        text = re.sub(
            r'(from PyQt5\.QtWidgets import \()',
            'from src.gui.themes import token, Typography\n\\1',
            text, count=1
        )
        p.write_text(text, encoding="utf-8")
        results.append(f"FIXED_TOPLEVEL: tools/file_management/advanced_catalog/advanced_catalog_window.py -> {try_parse(p)}")

# Special: extraction_parameter_dialogs.py has no try: block either
p = ROOT / "tools/pdf_tools/dialogs/extraction_parameter_dialogs.py"
if not try_parse(p):
    text = p.read_text(encoding="utf-8")
    bad = "from src.gui.themes import token\n"
    if bad in text:
        text = text.replace(bad, "", 1)
        text = re.sub(
            r'(from PyQt5\.QtWidgets import \()',
            'from src.gui.themes import token\n\\1',
            text, count=1
        )
        p.write_text(text, encoding="utf-8")
        results.append(f"FIXED_TOPLEVEL: tools/pdf_tools/dialogs/extraction_parameter_dialogs.py -> {try_parse(p)}")

# Special: permissions_editor.py also no try: block
p = ROOT / "tools/system/permissions/permissions_editor.py"
if not try_parse(p):
    text = p.read_text(encoding="utf-8")
    bad = "from src.gui.themes import token\n"
    if bad in text:
        text = text.replace(bad, "", 1)
        text = re.sub(
            r'(from PyQt5\.QtWidgets import \()',
            'from src.gui.themes import token\n\\1',
            text, count=1
        )
        p.write_text(text, encoding="utf-8")
        results.append(f"FIXED_TOPLEVEL2: tools/system/permissions/permissions_editor.py -> {try_parse(p)}")

# Special: privacy/privacy_cleaner/system_cleanup_gui.py
# Has stray code after sys.exit() in __main__ block - all after sys.exit() should be dropped
p = ROOT / "tools/privacy/privacy_cleaner/system_cleanup_gui.py"
if not try_parse(p):
    text = p.read_text(encoding="utf-8")
    bad = "from src.gui.themes import token\n"
    if bad in text:
        # Remove the misplaced import first
        text = text.replace(bad, "", 1)
    # Check for the stray orphaned code after sys.exit()
    # The file ends with sys.exit() then stray code
    # Truncate at sys.exit(app.exec_()) in the __main__ block
    if try_parse(p):
        p.write_text(text, encoding="utf-8")
        results.append(f"FIXED_CLEANUP: privacy/privacy_cleaner/system_cleanup_gui.py -> {try_parse(p)}")
    else:
        # Find and remove orphaned method definitions after sys.exit()
        # Pattern: sys.exit(app.exec_())  then orphaned code
        m = re.search(r'(    sys\.exit\(app\.exec_\(\)\)\n)', text)
        if m:
            end_pos = m.end()
            text = text[:end_pos]
        p.write_text(text, encoding="utf-8")
        results.append(f"FIXED_TRUNCATE: privacy/privacy_cleaner/system_cleanup_gui.py -> {try_parse(p)}")

# Special: filesystem_integrity_widget.py - Typography after 'from PyQt5.QtWidgets import QApplication'
p = ROOT / "tools/system/diagnostics_monitoring/gui/filesystem_integrity_widget.py"
if not try_parse(p):
    text = p.read_text(encoding="utf-8")
    bad = "from src.gui.themes import Typography\n"
    # Find it and see if it's misindented
    idx = text.find(bad)
    if idx >= 0:
        # Check indent
        line_start = text.rfind('\n', 0, idx) + 1
        indent = len(text[line_start:idx])
        if indent == 0:
            # At column 0 - inside an if __name__ == "__main__": block - needs 8 spaces
            text = text[:idx] + "        " + bad + text[idx + len(bad):]
            p.write_text(text, encoding="utf-8")
            results.append(f"FIXED_INDENT: diagnostics_monitoring/gui/filesystem_integrity_widget.py -> {try_parse(p)}")
        else:
            results.append(f"UNKNOWN_FS: indent={indent}")

# Special: metadata_indexing_system.py - 'MetadataExtractionResult:' orphan line
p = ROOT / "tools/file_management/advanced_folders/core/metadata_indexing_system.py"
if not try_parse(p):
    text = p.read_text(encoding="utf-8")
    # Remove the orphaned 'MetadataExtractionResult:' line that's a stray label
    text = re.sub(r'\n        MetadataExtractionResult:\n', '\n', text)
    p.write_text(text, encoding="utf-8")
    results.append(f"FIXED_ORPHAN: tools/file_management/advanced_folders/core/metadata_indexing_system.py -> {try_parse(p)}")

# Report all
for r in results:
    print(r)

# Final scan
print("\n=== REMAINING SYNTAX ERRORS ===")
broken = []
for py in sorted(ROOT.rglob("*.py")):
    try:
        ast.parse(py.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError as e:
        broken.append(f"{py.relative_to(ROOT.parent)}:{e.lineno}: {e.msg}")
print(f"Count: {len(broken)}")
for b in broken:
    print(b)
