import ast
from pathlib import Path
import re

ROOT = Path("C:/Users/HP1/1_2/src")

def fix_line_continuation_v6(p: Path):
    text = p.read_text(encoding="utf-8")
    # This matches \ then any non-newline characters until a newline
    new_text = re.sub(r'\\ [^\r\n]+(\r?\n)', r'\\\1', text)
    if new_text != text:
        p.write_text(new_text, encoding="utf-8")
        return True
    return False

# Target problematic lines
for rel in ["tools/file_management/advanced_folders/core/search_cache.py", 
            "tools/file_management/advanced_folders/gui/configuration_dialog.py",
            "tools/file_management/advanced_folders/gui/directory_browser.py"]:
    fix_line_continuation_v6(ROOT / rel)

def fix_try_import_final(p: Path):
    text = p.read_text(encoding="utf-8")
    # Search for try: block with misplaced col-0 import
    # This regex looks for try: followed by an import at col 0
    new_text = re.sub(r'try:\nfrom src\.gui\.themes import (.+)\n', r'try:\n    from src.gui.themes import \1\n', text)
    if new_text != text:
        p.write_text(new_text, encoding="utf-8")
        return True
    return False

for rel in ["tools/security/password_generator/password_generator.py", "tools/system/software_maintenance/gui/maintenance_hub.py"]:
    fix_try_import_final(ROOT / rel)

# Final check
print("\n=== FINAL RE-CHECK ===")
broken = []
for py in sorted(ROOT.rglob("*.py")):
    try:
        ast.parse(py.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError as e:
        broken.append(f"{py.relative_to(ROOT.parent)}:{e.lineno}: {e.msg}")
print(f"Count: {len(broken)}")
for b in broken:
    print(b)
