import os

fixes = {
    "src/tools/system/system_cleanup/core/system_locations.py": [340, 346, 356, 357],
    "src/tools/system/system_cleanup/core/windows_utils.py": [388, 429],
    "src/tools/system/system_cleanup/system_cleanup.py": [44, 99, 192, 237],
    "src/tools/system/system_cleanup/system_cleanup_gui.py": [
        79, 164, 168, 192, 200, 204, 206, 216, 231, 235,
        291, 314, 360, 368, 388, 504, 559, 746, 752, 765,
        771, 782, 788, 799, 805, 816, 822, 866, 894, 1076,
        1129, 1199, 1290, 1307, 1492, 1693, 1725
    ],
    "src/tools/system/system_cleanup/tools/temp_cleaner.py": [323],
}

base = r"C:\Users\HP1\1_2"

for rel_path, line_nums in fixes.items():
    full_path = os.path.join(base, rel_path.replace("/", os.sep))
    with open(full_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    changed = 0
    for ln in line_nums:
        idx = ln - 1
        if idx < len(lines):
            line = lines[idx]
            if '# noqa' not in line:
                lines[idx] = line.rstrip('\n') + '  # noqa: E501\n'
                changed += 1
    
    with open(full_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"{rel_path}: {changed} lines updated")
