#!/usr/bin/env python3
"""
check_component_usage.py — UI/UX Harmonization Check #2

Validates that tool source files use Hub-provided shared components
(PrimaryButton, SecondaryButton, TextInput, Modal, ToastNotification,
Breadcrumb, LoadingIndicator) rather than bare Qt widget equivalents,
OR that any direct Qt usage is documented in DEVIATIONS.md.

Exit codes:
  0 — No violations (or --strict not set)
  1 — Violations found (only when --strict is set)
"""

import argparse
import ast
import json
import re
import sys
from pathlib import Path

# Shared component imports that satisfy the requirement
REQUIRED_IMPORT_PATTERNS = [
    re.compile(r"from\s+src\.gui\.components\s+import"),
    re.compile(r"from\s+src\.gui\.components\.\w+\s+import"),
]

# Direct Qt widget uses that should be replaced with shared components
# Maps bare Qt widget → expected shared component
BARE_WIDGET_PATTERNS = {
    "QPushButton": "PrimaryButton / SecondaryButton / DestructiveButton",
    "QLineEdit": "TextInput",
    "QDialog": "Modal / ConfirmationModal",
    "QProgressBar": "LoadingIndicator",
    "QLabel": None,  # QLabel itself is not replaced; skip false positives
}

# Files / dirs to exclude from scanning
EXCLUDED_PATHS = {
    "check_component_usage.py",
    "themes.py",
    "styles.py",
    "buttons.py",
    "inputs.py",
    "modal.py",
    "toast.py",
    "breadcrumb.py",
    "loading_indicator.py",
    "hub_error_screen.py",
    "component_guardian.py",
    "__init__.py",
}

EXCLUDED_DIRS = {
    "__pycache__",
    ".venv312",
    "venv",
    ".git",
    "backups",
    "tests",
    "components",  # the shared component library itself
    "core/guardian",  # guardian infrastructure
}

# Tools-only scan: only flag bare usage in tool source files (src/tools/)
TOOLS_SUBDIR = "src/tools"


def is_excluded(path: Path, root: Path) -> bool:
    if path.name in EXCLUDED_PATHS:
        return True
    relative = path.relative_to(root)
    for part in relative.parts:
        if part in EXCLUDED_DIRS:
            return True
    return False


def file_uses_shared_components(text: str) -> bool:
    """Return True if the file already imports from src.gui.components."""
    return any(p.search(text) for p in REQUIRED_IMPORT_PATTERNS)


def scan_file(path: Path, root: Path) -> list[dict]:
    """Return violation dicts for bare Qt widget usage in a tool file."""
    violations = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return violations

    has_shared_import = file_uses_shared_components(text)

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return violations

    lines = text.splitlines()

    class _WidgetCallVisitor(ast.NodeVisitor):
        def __init__(self):
            self.matches: list[tuple[int, str]] = []

        def visit_Call(self, node: ast.Call):
            widget_name = None
            if isinstance(node.func, ast.Name):
                widget_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                widget_name = node.func.attr
            if widget_name in BARE_WIDGET_PATTERNS and BARE_WIDGET_PATTERNS[widget_name] is not None:
                self.matches.append((node.lineno, widget_name))
            self.generic_visit(node)

    visitor = _WidgetCallVisitor()
    visitor.visit(tree)

    for lineno, widget in visitor.matches:
        source = lines[lineno - 1].rstrip() if 0 <= lineno - 1 < len(lines) else ""
        violations.append(
            {
                "file": str(path),
                "line": lineno,
                "bare_widget": widget,
                "expected_component": BARE_WIDGET_PATTERNS[widget],
                "has_shared_import": has_shared_import,
                "source": source,
                "status": (
                    "migrated_partial" if has_shared_import else "not_migrated"
                ),
            }
        )
    return violations


def load_deviations(root: Path) -> set[str]:
    """Return set of documented deviation scope strings from DEVIATIONS.md."""
    deviations_path = root / "docs" / "ui-ux-harmonization" / "DEVIATIONS.md"
    if not deviations_path.exists():
        return set()
    text = deviations_path.read_text(encoding="utf-8", errors="replace")
    scopes: set[str] = set()
    for line in text.splitlines():
        if "| **Scope** |" not in line:
            continue
        parts = [part.strip() for part in line.split("|")]
        if len(parts) >= 3:
            scope = parts[2].strip()
            if scope:
                scopes.add(scope)
    return scopes


def is_covered_by_deviation(path: Path, root: Path, deviation_scopes: set[str]) -> bool:
    """Return True when *path* is already documented as a deviation scope."""
    relative = path.relative_to(root).as_posix()
    filename = path.name
    for scope in deviation_scopes:
        if relative in scope or filename in scope:
            return True
    return False


def scan_directory(root: Path) -> list[dict]:
    """Scan tool files under src/tools/ for bare Qt widget usage."""
    all_violations = []
    tools_dir = root / TOOLS_SUBDIR
    if not tools_dir.exists():
        print(
            f"[COMPONENT] WARNING: {tools_dir} not found; nothing to scan.",
            file=sys.stderr,
        )
        return all_violations

    deviation_scopes = load_deviations(root)

    for py_file in sorted(tools_dir.rglob("*.py")):
        if is_excluded(py_file, root):
            continue
        if is_covered_by_deviation(py_file, root, deviation_scopes):
            continue
        violations = scan_file(py_file, root)
        all_violations.extend(violations)
    return all_violations


def aggregate_by_file(violations: list[dict]) -> dict[str, list[dict]]:
    aggregated: dict[str, list[dict]] = {}
    for v in violations:
        aggregated.setdefault(v["file"], []).append(v)
    return aggregated


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Hub shared component usage in tool source files."
    )
    parser.add_argument("--root", default=".", help="Workspace root directory")
    parser.add_argument("--strict", action="store_true", help="Exit 1 on violations")
    parser.add_argument("--json", dest="output_json", action="store_true")
    parser.add_argument(
        "--baseline", metavar="FILE", help="Write baseline to JSON file"
    )
    parser.add_argument(
        "--phase",
        default="1",
        help="Migration phase (1=report only, 3=enforce). Default: 1",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    violations = scan_directory(root)
    by_file = aggregate_by_file(violations)

    result = {
        "check": "component_usage",
        "description": "Bare Qt widget usage in tool files (should use shared components after Phase 3)",
        "scan_root": str(root / TOOLS_SUBDIR),
        "phase": args.phase,
        "note": "Phase 1 baseline — violations expected; enforce in Phase 3.",
        "total_files_with_violations": len(by_file),
        "total_violations": len(violations),
        "violations_by_file": {f: vs for f, vs in by_file.items()},
    }

    if args.output_json:
        print(json.dumps(result, indent=2))
    else:
        if violations:
            phase_note = (
                "(baseline — Phase 3 will enforce)"
                if args.phase == "1"
                else "(ENFORCEMENT active)"
            )
            print(
                f"[COMPONENT] {len(by_file)} file(s), {len(violations)} bare Qt widget reference(s) {phase_note}:"
            )
            for filepath, vs in list(by_file.items())[:20]:
                rel = Path(filepath).relative_to(root)
                widgets = {v["bare_widget"] for v in vs}
                print(f"  {rel}: {', '.join(sorted(widgets))}")
            if len(by_file) > 20:
                print(f"  ... and {len(by_file) - 20} more files")
        else:
            print("[COMPONENT] PASS — No bare Qt widget usage found in tool files.")

    if args.baseline:
        baseline_path = Path(args.baseline)
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        with open(baseline_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"[COMPONENT] Baseline written to {baseline_path}")

    # Only enforce in strict mode AND phase 3
    if args.strict and args.phase == "3" and violations:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
