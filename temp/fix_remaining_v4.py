import ast
from pathlib import Path
import re

ROOT = Path("C:/Users/HP1/1_2/src")

def fix_line_continuation_harder(p: Path):
    text = p.read_bytes().decode("utf-8", errors="ignore")
    # This matches a backslash, any number of spaces, and finally a newline (\n or \r\n)
    # We replace it with just the backslash and the newline
    new_text = re.sub(r'\\ +(\r?\n)', r'\\\1', text)
    if new_text != text:
        p.write_text(new_text, encoding="utf-8")
        return True
    return False

# Fix line continuations
for rel in ["tools/file_management/advanced_folders/core/search_cache.py", 
            "tools/file_management/advanced_folders/gui/configuration_dialog.py",
            "tools/file_management/advanced_folders/gui/directory_browser.py"]:
    fix_line_continuation_harder(ROOT / rel)

# Fix password_generator.py and maintenance_hub.py indentation - more robustly
def fix_indent(p: Path):
    text = p.read_text(encoding="utf-8")
    # Identify the try: block and ensure the following lines are indented by 4 spaces
    lines = text.splitlines()
    new_lines = []
    in_try = False
    for line in lines:
        if line.strip() == "try:":
            in_try = True
            new_lines.append(line)
            continue
        if in_try:
            if line.strip().startswith("from src.gui.themes"):
                new_lines.append("    " + line.lstrip())
                continue
            elif line.strip().startswith("from PyQt5"):
                new_lines.append("    " + line.lstrip())
                continue
            elif line.strip().startswith("except"):
                in_try = False
        new_lines.append(line)
    p.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

for rel in ["tools/security/password_generator/password_generator.py", "tools/system/software_maintenance/gui/maintenance_hub.py"]:
    fix_indent(ROOT / rel)

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
