import ast
import re
from pathlib import Path

p = Path(r"C:\Users\HP1\1_2\src\tools\file_management\advanced_folders\core\search_cache.py")
raw = p.read_bytes()

# The bytes are b"search_type\\\r\n\r\n"
# We need to replace b"\\\\\r\n\r\n" or similar with b"':" 
# Let's try to match the pattern: a single quote followed by word characters, then backslash, then any number of newlines.

new_raw = re.sub(rb"'(\w+)\\\s*\r?\n\s*\r?\n\s*", rb"'\1': ", raw)

p.write_bytes(new_raw)

try:
    ast.parse(p.read_text(encoding="utf-8", errors="replace"))
    print("search_cache.py: SYNTAX OK")
except SyntaxError as e:
    print(f"search_cache.py: STILL BROKEN line {e.lineno}: {e.msg}")
    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    for i in range(max(0, e.lineno-4), min(len(lines), e.lineno+2)):
        print(f"    {i+1}: {repr(lines[i])}")
