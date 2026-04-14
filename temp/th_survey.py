"""Survey TH-2 (LightColors/DarkColors), TH-3 (QFont with args), TH-5 (hub_nav_*) across tool files."""

import os
import re
from pathlib import Path

root = Path("src/tools")
ldc = []
qfont = []
hub_nav = []

for f in sorted(root.rglob("*.py")):
    try:
        txt = f.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue
    fp = str(f).replace(os.getcwd() + os.sep, "").replace("\\", "/")
    if "LightColors." in txt or "DarkColors." in txt:
        ldc.append(fp)
    # QFont with at least one argument (family string or size)
    if re.search(r'QFont\s*\(\s*["\']', txt):
        qfont.append(fp)
    if "hub_nav_" in txt:
        hub_nav.append(fp)

print(f"TH-2 LightColors/DarkColors: {len(ldc)}")
for x in ldc:
    print(f"  {x}")

print(f"\nTH-3 QFont with string arg: {len(qfont)}")
for x in qfont:
    print(f"  {x}")

print(f"\nTH-5 hub_nav_: {len(hub_nav)}")
if hub_nav:
    for x in hub_nav:
        print(f"  {x}")
else:
    print("  none")
