import ast
import re
from pathlib import Path

# Fix 1: search_cache.py
p = Path(r"C:\Users\HP1\1_2\src\tools\file_management\advanced_folders\core\search_cache.py")
raw = p.read_bytes()
print(f"search_cache.py before: {len(raw)} bytes")
if b"\\'" in raw:
    raw = raw.replace(b"\\'", b"'")
    print("  Fixed escaped single quotes")
if b'\\"' in raw:
    raw = raw.replace(b'\\"', b'"')
    print("  Fixed escaped double quotes")
if b'\\n' in raw:
    raw = raw.replace(b'\\n', b'\n')
    print("  Fixed escaped newlines")
p.write_bytes(raw)
try:
    ast.parse(p.read_text(encoding="utf-8", errors="replace"))
    print("  search_cache.py: SYNTAX OK")
except SyntaxError as e:
    print(f"  search_cache.py: STILL BROKEN line {e.lineno}: {e.msg}")

# Fix 2: maintenance_hub.py
p2 = Path(r"C:\Users\HP1\1_2\src\tools\system\software_maintenance\gui\maintenance_hub.py")
text = p2.read_text(encoding="utf-8")
bad_pattern = r'\n    from src\.gui\.themes import Typography\n(\s+with open)'
m = re.search(bad_pattern, text)
if m:
    text = text[:m.start()] + '\n' + text[m.start(1):]
    p2.write_text(text, encoding="utf-8")
    print("  maintenance_hub.py: removed misplaced Typography import")
else:
    old = "    import json\n    from src.gui.themes import Typography\n                    with open(file_path"
    new = "    import json\n                    with open(file_path"
    if old in text:
        text = text.replace(old, new)
        p2.write_text(text, encoding="utf-8")
        print("  maintenance_hub.py: direct replacement applied")
    else:
        print("  maintenance_hub.py: pattern not found, searching...")
        idx = text.find("from src.gui.themes import Typography")
        if idx >= 0:
            line_start = text.rfind('\n', 0, idx)
            line_end = text.find('\n', idx)
            print(f"  The line: {repr(text[line_start:line_end+1])}")

try:
    ast.parse(p2.read_text(encoding="utf-8", errors="replace"))
    print("  maintenance_hub.py: SYNTAX OK")
except SyntaxError as e:
    print(f"  maintenance_hub.py: STILL BROKEN line {e.lineno}: {e.msg}")
