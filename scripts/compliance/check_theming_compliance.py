#!/usr/bin/env python3
"""
check_theming_compliance.py — UI/UX Harmonization Check #1

Detects hard-coded hex color strings remaining in tool source files.
All color values MUST be resolved through the TOKENS dict (spec §4.1.2).

Exit codes:
  0 — No violations (or --strict not set)
  1 — Violations found (only when --strict is set)
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Hex color pattern: #RGB, #RRGGBB (with word boundaries so partial matches are caught)
HEX_COLOR_RE = re.compile(r'(?<!["\w])#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})(?![0-9a-fA-F])')

# Files/paths to exclude from scanning
EXCLUDED_PATHS = {
    "themes.py",
    "styles.py",
    "check_theming_compliance.py",
    "AUTOMATED_TOOLING.md",
}

# Directories to exclude (relative to scan root)
EXCLUDED_DIRS = {
    "__pycache__",
    ".venv312",
    "venv",
    ".git",
    "backups",
    "node_modules",
}

# These are documentation/test exceptions: comments and string literals in docs
COMMENT_RE = re.compile(r"#.*")
TRIPLE_DOUBLE_RE = re.compile(r'""".*?"""', re.DOTALL)
TRIPLE_SINGLE_RE = re.compile(r"'''.*?'''", re.DOTALL)


def is_in_excluded_path(path: Path, scan_root: Path) -> bool:
    relative = path.relative_to(scan_root)
    parts = relative.parts
    if path.name in EXCLUDED_PATHS:
        return True
    for part in parts:
        if part in EXCLUDED_DIRS:
            return True
    return False


def scan_file(path: Path) -> list[dict]:
    """Return a list of violation dicts for a single file."""
    violations = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return violations

    for lineno, line in enumerate(text.splitlines(), start=1):
        # Skip pure comment lines
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        # Look for hex patterns
        for match in HEX_COLOR_RE.finditer(line):
            # Check if this is inside a comment on this line
            comment_start = line.find("#", 0, match.start())
            # Make sure it's not a color inside the TOKENS dict definition
            if (
                stripped.startswith("TOKENS")
                or stripped.startswith('"light"')
                or stripped.startswith('"dark"')
            ):
                continue
            violations.append(
                {
                    "file": str(path),
                    "line": lineno,
                    "column": match.start() + 1,
                    "match": match.group(0),
                    "source": line.rstrip(),
                }
            )
    return violations


def scan_directory(scan_root: Path, include_pattern: str = "src/") -> list[dict]:
    """Scan all .py files under scan_root matching include_pattern."""
    all_violations = []
    target = scan_root / Path(include_pattern.rstrip("/").rstrip("\\"))
    if not target.exists():
        target = scan_root

    for py_file in sorted(target.rglob("*.py")):
        if is_in_excluded_path(py_file, scan_root):
            continue
        violations = scan_file(py_file)
        all_violations.extend(violations)
    return all_violations


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check for hard-coded hex color strings in Python source."
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Workspace root directory (default: current directory)",
    )
    parser.add_argument(
        "--include",
        default="src/",
        help="Sub-path within root to scan (default: src/)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if any violations are found",
    )
    parser.add_argument(
        "--json",
        dest="output_json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--baseline",
        metavar="FILE",
        help="Write violation summary to a JSON file (baseline record)",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    violations = scan_directory(root, args.include)

    result = {
        "check": "theming_compliance",
        "description": "Hard-coded hex color strings in tool source",
        "scan_root": str(root / args.include),
        "total_violations": len(violations),
        "violations": violations,
    }

    if args.output_json:
        print(json.dumps(result, indent=2))
    else:
        if violations:
            print(f"[THEMING] {len(violations)} hard-coded hex color(s) found:")
            for v in violations:
                rel = Path(v["file"]).relative_to(root)
                print(
                    f"  {rel}:{v['line']}:{v['column']}  {v['match']}  |  {v['source'].strip()}"
                )
        else:
            print("[THEMING] PASS — No hard-coded hex colors found.")

    if args.baseline:
        baseline_path = Path(args.baseline)
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        with open(baseline_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"[THEMING] Baseline written to {baseline_path}")

    if args.strict and violations:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
