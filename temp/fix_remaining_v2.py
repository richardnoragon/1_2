import ast
from pathlib import Path
import re

ROOT = Path("C:/Users/HP1/1_2/src")

def strip_spaces_after_backslash(p: Path):
    text = p.read_text(encoding="utf-8")
    new_text = re.sub(r'\\\s+\n', r'\\\n', text)
    if new_text != text:
        p.write_text(new_text, encoding="utf-8")
        return True
    return False

# Fix line continuations
for rel in ["tools/file_management/advanced_folders/core/search_cache.py", 
            "tools/file_management/advanced_folders/gui/configuration_dialog.py",
            "tools/file_management/advanced_folders/gui/directory_browser.py"]:
    strip_spaces_after_backslash(ROOT / rel)

# Fix password_generator.py and maintenance_hub.py manually
# These ones had misplaced token import and missing except
def fix_mangled_try(p: Path, import_line: str):
    text = p.read_text(encoding="utf-8")
    # Identify the misplaced line
    bad = import_line + "\n"
    if bad in text:
        text = text.replace(bad, "", 1)
    
    # Structure it correctly
    # Strategy: Find the start of the try: block, and put everything in it
    # then add the except: block
    match = re.search(r'try:\n(\s+from PyQt5.+\n)+', text)
    if match:
        start = match.start()
        end = match.end()
        pyqt_part = text[start:end]
        # Reinject the import_line inside the try block
        new_try = pyqt_part.replace("try:\n", "try:\n    " + import_line + "\n", 1)
        # Ensure it has an except:
        rest = text[end:]
        if not rest.strip().startswith("except"):
            new_try += "except ImportError:\n    pass\n"
        
        new_text = text[:start] + new_try + rest
        p.write_text(new_text, encoding="utf-8")

fix_mangled_try(ROOT / "tools/security/password_generator/password_generator.py", "from src.gui.themes import token")
fix_mangled_try(ROOT / "tools/system/software_maintenance/gui/maintenance_hub.py", "from src.gui.themes import token")

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
