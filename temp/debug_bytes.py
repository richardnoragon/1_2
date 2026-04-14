from pathlib import Path
p = Path(r"C:\Users\HP1\1_2\src\tools\file_management\advanced_folders\core\search_cache.py")
raw = p.read_bytes()
print(f"Bytes around line 748: {repr(raw[raw.find(b'search_type'):raw.find(b'search_type')+50])}")
