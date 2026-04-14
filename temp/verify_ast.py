import ast
from pathlib import Path

ROOT = Path("C:/Users/HP1/1_2/src")
broken = []
ok = 0
for py in sorted(ROOT.rglob("*.py")):
    try:
        ast.parse(py.read_text(encoding="utf-8", errors="ignore"))
        ok += 1
    except SyntaxError as e:
        broken.append(f"{py.relative_to(ROOT.parent)}:{e.lineno}: {e.msg}")

print(f"OK: {ok}")
print(f"BROKEN: {len(broken)}")
for b in broken:
    print(b)
