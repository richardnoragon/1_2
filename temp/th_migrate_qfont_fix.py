"""Fix remaining QFont patterns with QFont.Bold/Weight argument."""

import re
from pathlib import Path

SIZE_TO_METHOD = {
    18: "h1",
    16: "h1",
    15: "h1",
    14: "h2",
    13: "h2",
    12: "h3",
    11: "h3",
    10: "body",
    9: "body",
    8: "caption",
    7: "caption",
}

# Quoted-family patterns (handles single/double quotes)
PAT3 = re.compile(r'QFont\s*\(\s*["\'][^"\']*["\']\s*,\s*(\d+)\s*,\s*[\w.]+\s*\)')
PAT2 = re.compile(r'QFont\s*\(\s*["\'][^"\']*["\']\s*,\s*(\d+)\s*\)')
PAT1 = re.compile(r'QFont\s*\(\s*["\'][^"\']*["\']\s*\)')
PAT0 = re.compile(r"QFont\s*\(\s*\)")

IMPORT_PAT = re.compile(r"from src\.gui\.themes import")


def _repl3(m):
    sz = int(m.group(1))
    method = SIZE_TO_METHOD.get(sz, "body")
    return f"Typography.{method}()"


def _repl2(m):
    sz = int(m.group(1))
    method = SIZE_TO_METHOD.get(sz, "body")
    return f"Typography.{method}()"


def fix_qfont(txt):
    count = [0]

    def r3(m):
        count[0] += 1
        return _repl3(m)

    def r2(m):
        count[0] += 1
        return _repl2(m)

    def r1(m):
        count[0] += 1
        return "Typography.body()"

    def r0(m):
        count[0] += 1
        return "Typography.body()"

    txt = PAT3.sub(r3, txt)
    txt = PAT2.sub(r2, txt)
    txt = PAT1.sub(r1, txt)
    txt = PAT0.sub(r0, txt)
    return txt, count[0]


TARGET_FILES = [
    "src/tools/file_management/advanced_catalog/advanced_catalog_window.py",
    "src/tools/file_management/advanced_folders/ui/advanced_folders_widget.py",
    "src/tools/system/process_monitor/process_monitor.py",
    "src/tools/system/simple_system_info.py",
    "src/tools/security/security_scanner/security_scanner.py",
    "src/tools/system/diagnostics_monitoring/gui/filesystem_integrity_widget.py",
    "src/tools/system/diagnostics_monitoring/gui/performance_widget.py",
]

total = 0
for fp in TARGET_FILES:
    p = Path(fp)
    if not p.exists():
        print(f"  MISSING  {fp}")
        continue
    txt = p.read_text(encoding="utf-8", errors="ignore")
    new_txt, n = fix_qfont(txt)
    if n > 0:
        # Inject Typography import if missing
        if "Typography" not in new_txt or "from src.gui.themes" not in new_txt:
            inject = "from src.gui.themes import Typography\n"
            lines = new_txt.splitlines(keepends=True)
            idx = 0
            for i, ln in enumerate(lines):
                if ln.strip().startswith(("import ", "from ")):
                    idx = i + 1
            lines.insert(idx, inject)
            new_txt = "".join(lines)
        elif (
            "from src.gui.themes import" in new_txt
            and "Typography"
            not in new_txt.split("from src.gui.themes import")[1].split("\n")[0]
        ):
            # themes import exists but doesn't include Typography — append it
            new_txt = re.sub(
                r"(from src\.gui\.themes import\s+)(\w+)",
                r"\1\2, Typography",
                new_txt,
                count=1,
            )
        p.write_text(new_txt, encoding="utf-8")
        print(f"  {n:2d} replacements  {fp}")
        total += n
    else:
        print(f"   0 replacements  {fp}  (no matches)")

print(
    f"\nTH-3 supplemental: {total} replacements across {sum(1 for _ in TARGET_FILES)} files checked"
)
