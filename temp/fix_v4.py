import ast
from pathlib import Path

p = Path(r"C:\Users\HP1\1_2\src\tools\file_management\advanced_folders\core\search_cache.py")
text = p.read_text(encoding="utf-8", errors="replace").splitlines()

# The original code looks like:
# 'search_type': parameters.search_type.value if parameters.search_type else None,
# But it was split into multiple lines with trailing commas and extra parentheses.

# Let's rewrite the dictionary manually to be sure it's correct.
start_idx = -1
end_idx = -1
for i, line in enumerate(text):
    if 'param_dict = {' in line:
        start_idx = i
    if start_idx != -1 and '                self.db_path' in line:
        # the dict should end before this
        end_idx = i - 1
        break

if start_idx != -1 and end_idx != -1:
    print(f"Replacing lines {start_idx+1} to {end_idx+1}")
    new_lines = [
        "            param_dict = {",
        "                'query': parameters.query,",
        "                'search_type': parameters.search_type.value if parameters.search_type else None,",
        "                'root_paths': sorted(parameters.root_paths),",
        "                'max_depth': parameters.max_depth,",
        "                'recursive': parameters.recursive,",
        "                'follow_symlinks': parameters.follow_symlinks,",
        "                'file_patterns': sorted(parameters.file_patterns) if parameters.file_patterns else None,",
        "                'exclude_patterns': sorted(parameters.exclude_patterns) if parameters.exclude_patterns else None,",
        "                'min_size': parameters.min_size,",
        "                'max_size': parameters.max_size,",
        "                'modified_after': parameters.modified_after.isoformat() if parameters.modified_after else None,",
        "                'modified_before': parameters.modified_before.isoformat() if parameters.modified_before else None,",
        "            }"
    ]
    text[start_idx:end_idx] = new_lines
    p.write_text("\n".join(text), encoding="utf-8")

try:
    ast.parse(p.read_text(encoding="utf-8", errors="replace"))
    print("search_cache.py: SYNTAX OK")
except SyntaxError as e:
    print(f"search_cache.py: STILL BROKEN line {e.lineno}: {e.msg}")
    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    for i in range(max(0, e.lineno-4), min(len(lines), e.lineno+2)):
        print(f"    {i+1}: {repr(lines[i])}")
