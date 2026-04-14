#!/usr/bin/env python3
"""
run_compliance_checks.py — UI/UX Harmonization: Run All Three Checks

Runs all three automated compliance checks in sequence and produces a
combined summary suitable for CI output.

Usage:
  python scripts/compliance/run_compliance_checks.py [--root .] [--strict] [--baseline-dir results/compliance/]

Exit codes:
  0 — All checks passed (no violations, or --strict not set)
  1 — One or more checks found violations (only when --strict is set)
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

CHECKS = [
    {
        "name": "Theming Compliance",
        "id": "theming",
        "script": "scripts/compliance/check_theming_compliance.py",
        "baseline_file": "theming_baseline.json",
    },
    {
        "name": "Component Usage Validation",
        "id": "component",
        "script": "scripts/compliance/check_component_usage.py",
        "baseline_file": "component_baseline.json",
    },
    {
        "name": "Accessibility Scan",
        "id": "accessibility",
        "script": "scripts/compliance/check_accessibility.py",
        "baseline_file": "accessibility_baseline.json",
    },
]


def run_check(
    python_exe: str,
    script_path: Path,
    root: str,
    strict: bool,
    baseline_file: Path | None,
    phase: str = "1",
) -> tuple[int, dict]:
    """Run a single check script and return (exit_code, result_dict)."""
    cmd = [python_exe, str(script_path), "--root", root]
    if strict:
        cmd.append("--strict")
    if baseline_file:
        cmd.extend(["--baseline", str(baseline_file)])
    if "component" in str(script_path):
        cmd.extend(["--phase", phase])

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        # Print human-readable output from the sub-script
        if proc.stdout.strip():
            for line in proc.stdout.strip().splitlines():
                print(f"  {line}")
        if proc.stderr.strip():
            for line in proc.stderr.strip().splitlines():
                print(f"  [stderr] {line}")
        # Read result from the baseline file if it was written
        result: dict = {}
        if baseline_file and baseline_file.exists():
            try:
                with open(baseline_file, encoding="utf-8") as f:
                    result = json.load(f)
            except (json.JSONDecodeError, OSError):
                result = {"error": f"Could not read baseline file {baseline_file}"}
        if not result:
            result = {
                "error": proc.stderr or "no baseline file and no parseable output"
            }
        return proc.returncode, result
    except subprocess.TimeoutExpired:
        return 2, {"error": "Timed out after 120 seconds"}
    except Exception as e:
        return 3, {"error": str(e)}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run all UI/UX Harmonization compliance checks."
    )
    parser.add_argument("--root", default=".", help="Workspace root directory")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 if any check finds violations",
    )
    parser.add_argument(
        "--baseline-dir",
        default="results/compliance",
        metavar="DIR",
        help="Directory to write baseline JSON files (default: results/compliance/)",
    )
    parser.add_argument(
        "--phase",
        default="1",
        help="Migration phase for component check (1=report only, 3=enforce)",
    )
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Python interpreter to use for sub-checks",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    baseline_dir = root / args.baseline_dir
    baseline_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 65)
    print("UI/UX Harmonization — Automated Compliance Checks")
    print(f"Run time : {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"Root     : {root}")
    print(f"Phase    : {args.phase}")
    print(
        f"Mode     : {'STRICT (will fail CI on violations)' if args.strict else 'REPORT ONLY'}"
    )
    print("=" * 65)

    combined_results = []
    any_failed = False

    for check in CHECKS:
        script = root / check["script"]
        baseline_path = baseline_dir / check["baseline_file"]
        print(f"\n--- {check['name']} ---")

        exit_code, result = run_check(
            args.python,
            script,
            str(root),
            args.strict,
            baseline_path,
            args.phase,
        )

        status = "PASS" if exit_code == 0 else "FAIL"
        total = result.get("total_violations", "?")
        print(f"  Status : {status}")
        print(f"  Violations : {total}")

        if exit_code != 0:
            any_failed = True

        combined_results.append(
            {
                "check_id": check["id"],
                "check_name": check["name"],
                "exit_code": exit_code,
                "status": status,
                "result": result,
            }
        )

    # Write combined summary
    summary = {
        "run_time": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "phase": args.phase,
        "strict": args.strict,
        "overall_status": "FAIL" if any_failed else "PASS",
        "checks": combined_results,
    }
    summary_path = baseline_dir / "compliance_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 65)
    overall = "FAIL" if any_failed else "PASS"
    print(f"Overall: {overall}")
    print(f"Summary written to: {summary_path}")
    print("=" * 65)

    if args.strict and any_failed:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
