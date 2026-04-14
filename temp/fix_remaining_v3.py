import ast
from pathlib import Path
import re

ROOT = Path("C:/Users/HP1/1_2/src")

def fix_line_continuation_brute_force(p: Path):
    text = p.read_bytes().decode("utf-8", errors="ignore")
    # Actually just remove space after backslash before newline
    # Windows lines often have \r\n
    new_text = re.sub(r'\\\s+\r?\n', r'\\\n', text)
    if new_text != text:
        p.write_text(new_text, encoding="utf-8")
        return True
    return False

# Fix line continuations
for rel in ["tools/file_management/advanced_folders/core/search_cache.py", 
            "tools/file_management/advanced_folders/gui/configuration_dialog.py",
            "tools/file_management/advanced_folders/gui/directory_browser.py"]:
    fix_line_continuation_brute_force(ROOT / rel)

# Fix password_generator.py and maintenance_hub.py indentation
for rel in ["tools/security/password_generator/password_generator.py", "tools/system/software_maintenance/gui/maintenance_hub.py"]:
    p = ROOT / rel
    text = p.read_text(encoding="utf-8")
    # Fix 'unexpected indent' by ensuring 4-space indent for the line after try:
    new_text = re.sub(r'try:\n\s+from src\.gui\.themes import token', 'try:\n    from src.gui.themes import token', text)
    p.write_text(new_text, encoding="utf-8")

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
