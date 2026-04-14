from pathlib import Path
p = Path(r"C:\Users\HP1\1_2\src\tools\file_management\advanced_folders\core\search_cache.py")
text = p.read_text(encoding="utf-8", errors="replace").splitlines()
for i, line in enumerate(text):
    if 'param_dict = {' in line:
        print(f"Start found at line {i+1}: {line}")
    if 'self.db_path' in line:
        print(f"End context found at line {i+1}: {line}")
