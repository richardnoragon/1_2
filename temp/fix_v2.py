import ast
from pathlib import Path

p = Path(r"C:\Users\HP1\1_2\src\tools\file_management\advanced_folders\core\search_cache.py")
text = p.read_text(encoding="utf-8", errors="replace")

# The issues seem to be 'search_type\" followed by a newline or similar.
# Let's fix these specific broken dictionary keys.
text = text.replace("'search_type\\\"", "'search_type':")
text = text.replace("'root_paths\\\"", "'root_paths':")
text = text.replace("'max_depth\\\"", "'max_depth':")
text = text.replace("'recursive\\\"", "'recursive':")
text = text.replace("'follow_symlinks\\\"", "'follow_symlinks':")
text = text.replace("'file_patterns\\\"", "'file_patterns':")
text = text.replace("'exclude_patterns\\\"", "'exclude_patterns':")
text = text.replace("'min_size\\\"", "'min_size':")
text = text.replace("'max_size\\\"", "'max_size':")
text = text.replace("'modified_after\\\"", "'modified_after':")
text = text.replace("'modified_before\\\"", "'modified_before':")

p.write_text(text, encoding="utf-8")

try:
    ast.parse(p.read_text(encoding="utf-8", errors="replace"))
    print("search_cache.py: SYNTAX OK")
except SyntaxError as e:
    print(f"search_cache.py: STILL BROKEN line {e.lineno}: {e.msg}")
    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    for i in range(max(0, e.lineno-4), min(len(lines), e.lineno+2)):
        print(f"    {i+1}: {repr(lines[i])}")

