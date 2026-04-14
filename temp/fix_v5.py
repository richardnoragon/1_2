import ast
from pathlib import Path

p = Path(r"C:\Users\HP1\1_2\src\tools\file_management\advanced_folders\core\search_cache.py")
text = p.read_text(encoding="utf-8", errors="replace").splitlines()

# Correct version of the param_dict dictionary based on fields found in inspect_v2.py
new_dict_block = [
    "            param_dict = {",
    "                'query': parameters.query,",
    "                'search_type': parameters.search_type.value if parameters.search_type else None,",
    "                'root_paths': sorted(parameters.root_paths) if parameters.root_paths else [],",
    "                'case_sensitive': parameters.case_sensitive,",
    "                'include_subdirectories': parameters.include_subdirectories,",
    "                'file_type_filter': {",
    "                    'include_extensions': sorted(parameters.file_type_filter.include_extensions) if parameters.file_type_filter.include_extensions else [],",
    "                    'exclude_extensions': sorted(parameters.file_type_filter.exclude_extensions) if parameters.file_type_filter.exclude_extensions else [],",
    "                    'mime_types': sorted(parameters.file_type_filter.mime_types) if parameters.file_type_filter.mime_types else []",
    "                } if parameters.file_type_filter else None",
    "            }"
]

# Replacement range from line 746 to 777
start_idx = 745 # 0-indexed for line 746
end_idx = 777    # replace up to and including line 777

text[start_idx:end_idx] = new_dict_block
p.write_text("\n".join(text), encoding="utf-8")

try:
    ast.parse(p.read_text(encoding="utf-8", errors="replace"))
    print("search_cache.py: SYNTAX OK")
except SyntaxError as e:
    print(f"search_cache.py: STILL BROKEN line {e.lineno}: {e.msg}")
