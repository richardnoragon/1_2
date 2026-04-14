"""Spot-check migration quality."""

import re
from pathlib import Path

HEX_PAT = re.compile(r"#[0-9a-fA-F]{3,8}")

files = [
    "src/tools/file_management/advanced_folders/gui/preview_pane.py",
    "src/tools/pdf_tools/dialogs/parameter_dialogs.py",
    "src/tools/pdf_tools/widgets/enhanced_pdf_tools_widget.py",
    "src/gui/safe_standard_window.py",
]

for fp in files:
    p = Path(fp)
    txt = p.read_text(encoding="utf-8", errors="ignore")
    # import check
    import_ok = "from src.gui.themes import" in txt
    # token call count
    token_calls = len(re.findall(r"token\(", txt))
    # remaining hex (inside string literals only, crude)
    lines = txt.splitlines()
    hex_lines = [
        (i + 1, l.strip())
        for i, l in enumerate(lines)
        if HEX_PAT.search(l) and not l.strip().startswith("#")
    ]
    print(f"\n{'='*60}")
    print(f"FILE: {fp}")
    print(f"  themes import: {import_ok}")
    print(f"  token() calls: {token_calls}")
    print(f"  remaining hex lines: {len(hex_lines)}")
    for lno, ln in hex_lines[:5]:
        print(f"    L{lno}: {ln[:80]}")
