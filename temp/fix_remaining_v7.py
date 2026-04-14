import ast
from pathlib import Path

ROOT = Path("C:/Users/HP1/1_2/src")

# 1. Fix password_generator.py and maintenance_hub.py manually
files = [
    "tools/security/password_generator/password_generator.py",
    "tools/system/software_maintenance/gui/maintenance_hub.py"
]
for rel in files:
    p = ROOT / rel
    lines = p.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        if line.strip() == "try:" and i+1 < len(lines):
            if lines[i+1].startswith("from src.gui.themes"):
                lines[i+1] = "    " + lines[i+1]
                print(f"Fixed {rel}")
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")

# 2. Fix line continuation characters
lc_files = [
    "tools/file_management/advanced_folders/core/search_cache.py",
    "tools/file_management/advanced_folders/gui/configuration_dialog.py",
    "tools/file_management/advanced_folders/gui/directory_browser.py"
]
for rel in lc_files:
    p = ROOT / rel
    lines = p.read_text(encoding="utf-8").splitlines()
    new_lines = []
    for line in lines:
        if "\\" in line:
            # Drop everything after the last backslash
            idx = line.rfind("\\")
            new_lines.append(line[:idx+1])
        else:
            new_lines.append(line)
    p.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    print(f"Fixed {rel}")

# Final re-check
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
