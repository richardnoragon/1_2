from pathlib import Path
p = Path(r"C:\Users\HP1\1_2\src\tools\file_management\advanced_folders\core\search_cache.py")
text = p.read_text(encoding="utf-8", errors="replace").splitlines()
for i in range(743, 755):
    if i < len(text):
        print(f"{i+1}: {repr(text[i])}")
