#!/usr/bin/env python3
"""
check_accessibility.py — UI/UX Harmonization Check #3

Scans tool source files to detect interactive Qt widgets that do NOT have
a corresponding setAccessibleName() call in the same class/function block.
All interactive controls MUST carry accessible labels (spec §6.1).

Checks performed:
  - QPushButton, QToolButton, QCheckBox, QRadioButton, QComboBox,
    QSpinBox, QDoubleSpinBox, QLineEdit, QTextEdit, QPlainTextEdit,
    QListWidget, QTreeWidget, QTableWidget, QSlider
    → each MUST have setAccessibleName() called nearby

Exit codes:
  0 — No violations (or --strict not set)
  1 — Violations found (only when --strict is set)
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Interactive widgets that MUST have setAccessibleName()
INTERACTIVE_WIDGETS = {
    "QPushButton",
    "QToolButton",
    "QCheckBox",
    "QRadioButton",
    "QComboBox",
    "QSpinBox",
    "QDoubleSpinBox",
    "QLineEdit",
    "QTextEdit",
    "QPlainTextEdit",
    "QListWidget",
    "QTreeWidget",
    "QTableWidget",
    "QSlider",
    "QTabWidget",
}

# Widgets from the shared component library that pre-set accessible names
# (they call setAccessibleName internally — no double-requirement needed)
SHARED_COMPONENT_WIDGETS = {
    "PrimaryButton",
    "SecondaryButton",
    "DestructiveButton",
    "TextInput",
    "Modal",
    "ConfirmationModal",
    "ToastNotification",
    "Breadcrumb",
    "LoadingIndicator",
    "HubErrorScreen",
}

EXCLUDED_DIRS = {
    "__pycache__",
    ".venv312",
    "venv",
    ".git",
    "backups",
    "tests",
    "components",  # shared library — already sets names
    "core/guardian",
}

EXCLUDED_FILES = {
    "check_accessibility.py",
    "themes.py",
    "styles.py",
    "__init__.py",
}

TOOLS_SUBDIR = "src/tools"

# Window to check: if a widget assignment is found, look within ±CONTEXT_LINES
# for a setAccessibleName() call on the same variable name
CONTEXT_LINES = 20

WIDGET_ASSIGN_RE = re.compile(
    r"(\w+)\s*=\s*(?:" + "|".join(re.escape(w) for w in INTERACTIVE_WIDGETS) + r")\s*\("
)
ACCESSIBLE_NAME_RE = re.compile(r"setAccessibleName\s*\(")


def is_excluded(path: Path, root: Path) -> bool:
    if path.name in EXCLUDED_FILES:
        return True
    relative = path.relative_to(root)
    for part in relative.parts:
        if part in EXCLUDED_DIRS:
            return True
    return False


def scan_file(path: Path, root: Path) -> list[dict]:
    """Detect interactive widget assignments without nearby setAccessibleName() calls."""
    violations = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return violations

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        match = WIDGET_ASSIGN_RE.search(line)
        if not match:
            continue

        var_name = match.group(1)
        if var_name in ("self", "super", "parent"):
            continue  # skip chained calls

        # Check context window for setAccessibleName on this variable
        start = max(0, i - 2)
        end = min(len(lines), i + CONTEXT_LINES + 1)
        context_text = "\n".join(lines[start:end])

        accessible_pattern = re.compile(
            rf"{re.escape(var_name)}\s*\.\s*setAccessibleName\s*\("
        )
        # Also accept self.var_name.setAccessibleName
        self_accessible_pattern = re.compile(
            rf"self\s*\.\s*{re.escape(var_name)}\s*\.\s*setAccessibleName\s*\("
        )

        if not (
            accessible_pattern.search(context_text)
            or self_accessible_pattern.search(context_text)
            or ACCESSIBLE_NAME_RE.search(line)
        ):
            violations.append(
                {
                    "file": str(path),
                    "line": i + 1,
                    "variable": var_name,
                    "widget_type": match.group(0)
                    .split("=")[1]
                    .strip()
                    .split("(")[0]
                    .strip(),
                    "source": line.rstrip(),
                }
            )

    return violations


def scan_directory(root: Path) -> list[dict]:
    """Scan all Python files under src/ for accessibility violations."""
    all_violations = []
    scan_root = root / "src"
    if not scan_root.exists():
        scan_root = root

    for py_file in sorted(scan_root.rglob("*.py")):
        if is_excluded(py_file, root):
            continue
        violations = scan_file(py_file, root)
        all_violations.extend(violations)
    return all_violations


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Detect interactive Qt widgets missing setAccessibleName() calls."
    )
    parser.add_argument("--root", default=".", help="Workspace root directory")
    parser.add_argument("--strict", action="store_true", help="Exit 1 on violations")
    parser.add_argument("--json", dest="output_json", action="store_true")
    parser.add_argument(
        "--baseline", metavar="FILE", help="Write baseline to JSON file"
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    violations = scan_directory(root)

    # Group by file for display
    by_file: dict[str, list[dict]] = {}
    for v in violations:
        by_file.setdefault(v["file"], []).append(v)

    result = {
        "check": "accessibility",
        "description": "Interactive Qt widgets missing setAccessibleName() calls",
        "scan_root": str(root / "src"),
        "total_files_with_violations": len(by_file),
        "total_violations": len(violations),
        "violations_by_file": by_file,
    }

    if args.output_json:
        print(json.dumps(result, indent=2))
    else:
        if violations:
            print(
                f"[A11Y] {len(by_file)} file(s), "
                f"{len(violations)} widget(s) missing setAccessibleName():"
            )
            for filepath, vs in list(by_file.items())[:20]:
                rel = Path(filepath).relative_to(root)
                print(f"  {rel}: {len(vs)} widget(s)")
                for v in vs[:3]:
                    print(
                        f"    line {v['line']}: {v['widget_type']} -> {v['variable']}"
                    )
                if len(vs) > 3:
                    print(f"    ... and {len(vs) - 3} more")
            if len(by_file) > 20:
                print(f"  ... and {len(by_file) - 20} more files")
        else:
            print("[A11Y] PASS — All interactive widgets have setAccessibleName().")

    if args.baseline:
        baseline_path = Path(args.baseline)
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        with open(baseline_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"[A11Y] Baseline written to {baseline_path}")

    if args.strict and violations:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
