import ast
from pathlib import Path
import re

ROOT = Path("C:/Users/HP1/1_2/src")

def fix_line_continuation_v5(p: Path):
    text = p.read_bytes()
    # Replace backslash + any number of spaces + \r\n (or \n) with just \r\n (or \n)
    # The error "unexpected character after line continuation character" means something is between \ and \n.
    new_text = re.sub(b'\\\\ +\\r?\\n', b'\\\\\n', text)
    if new_text != text:
        p.write_bytes(new_text)
        return True
    return False

for rel in ["tools/file_management/advanced_folders/core/search_cache.py", 
            "tools/file_management/advanced_folders/gui/configuration_dialog.py",
            "tools/file_management/advanced_folders/gui/directory_browser.py"]:
    fix_line_continuation_v5(ROOT / rel)

# Fix password_generator and maintenance_hub
# These files have:
# try:
# from src.gui.themes import token
#     from PyQt5...
# except...
#
# The "from src" line is at col 0, it should be indented 4 spaces.
def fix_mangled_try_v5(p: Path):
    lines = p.read_text(encoding="utf-8").splitlines()
    new_lines = []
    for i, line in enumerate(lines):
        if line.strip() == "try:":
            new_lines.append(line)
            # Check if next line is 'from src.gui.themes import token' at col 0
            if i+1 < len(lines) and lines[i+1].startswith("from src.gui.themes"):
                new_lines.append("    " + lines[i+1])
                lines[i+1] = "" # Skip it next iteration
            continue
        if line == "": continue
        new_lines.append(line)
    p.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

for rel in ["tools/security/password_generator/password_generator.py", "tools/system/software_maintenance/gui/maintenance_hub.py"]:
    fix_mangled_try_v5(ROOT / rel)

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
