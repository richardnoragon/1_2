"""
check_dependencies.py — Verify installed packages match requirements.txt (T045).

Usage:
    python scripts/check_dependencies.py [--requirements <file>] [--platform <platform>] [--check-undeclared]

Exit codes:
    0 — all declared packages match installed versions
    1 — one or more mismatches detected
"""

import argparse
import sys
from importlib.metadata import (
    PackageNotFoundError,
    packages_distributions,
    version,
)


def parse_requirements(filepath: str) -> dict[str, str]:
    """Parse requirements.txt into {package_name: required_version}."""
    reqs: dict[str, str] = {}
    try:
        with open(filepath, encoding="utf-8") as fh:
            for raw_line in fh:
                line = raw_line.split("#")[0].strip()
                if not line:
                    continue
                if "==" in line:
                    name, ver = line.split("==", 1)
                    reqs[name.strip()] = ver.strip()
    except FileNotFoundError:
        print(f"ERROR: requirements file not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    return reqs


def check_installed(reqs: dict[str, str]) -> list[str]:
    """Return list of MISMATCH lines for packages that don't match."""
    mismatches: list[str] = []
    for package, required_ver in reqs.items():
        try:
            installed_ver = version(package)
            if installed_ver != required_ver:
                mismatches.append(
                    f"MISMATCH {package}: required=={required_ver} installed=={installed_ver}"
                )
        except PackageNotFoundError:
            mismatches.append(
                f"MISMATCH {package}: required=={required_ver} installed==<not found>"
            )
    return mismatches


def check_undeclared(reqs: dict[str, str]) -> list[str]:
    """Return list of packages installed but not declared in requirements."""
    declared = {name.lower() for name in reqs}
    try:
        dist_map = packages_distributions()
    except Exception:
        return []
    undeclared = []
    seen: set[str] = set()
    for pkg in dist_map:
        pkg_lower = pkg.lower()
        if pkg_lower not in declared and pkg_lower not in seen:
            seen.add(pkg_lower)
            undeclared.append(f"UNDECLARED {pkg}")
    return undeclared


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify installed package versions.")
    parser.add_argument(
        "--requirements", default="requirements.txt", help="Path to requirements file"
    )
    parser.add_argument(
        "--platform", default=None, help="Platform hint (informational only)"
    )
    parser.add_argument(
        "--check-undeclared",
        action="store_true",
        help="Also report packages installed but not declared",
    )
    args = parser.parse_args()

    if args.platform:
        print(f"Platform: {args.platform}")

    reqs = parse_requirements(args.requirements)
    print(f"Checking {len(reqs)} declared packages from {args.requirements} ...")

    issues = check_installed(reqs)

    if args.check_undeclared:
        issues += check_undeclared(reqs)

    for line in issues:
        print(line)

    if issues:
        print(f"\n{len(issues)} issue(s) found.")
        return 1

    print("All declared packages match.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
