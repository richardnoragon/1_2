#!/usr/bin/env python3
"""Project-level quality gate runner for tests and coverage enforcement."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


DEFAULT_COVERAGE_THRESHOLD = 75


def build_pytest_command(test_targets: list[str], coverage_threshold: int) -> list[str]:
    command = [
        sys.executable,
        "-m",
        "pytest",
        *test_targets,
        "-q",
        "--maxfail=1",
        "--strict-markers",
        "--strict-config",
        "--disable-warnings",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=xml",
        f"--cov-fail-under={coverage_threshold}",
    ]
    return command


def run_command(command: list[str], cwd: Path) -> int:
    env = os.environ.copy()
    env.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    result = subprocess.run(command, cwd=str(cwd), env=env)
    return int(result.returncode)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the RFU quality gate checks.")
    parser.add_argument(
        "targets",
        nargs="*",
        default=["tests/unit/core"],
        help="Pytest targets to run. Defaults to the core unit tests folder.",
    )
    parser.add_argument(
        "--coverage-threshold",
        type=int,
        default=DEFAULT_COVERAGE_THRESHOLD,
        help=f"Minimum coverage threshold required for the gate (default: {DEFAULT_COVERAGE_THRESHOLD}%).",
    )
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Skip coverage enforcement for a lightweight smoke pass.",
    )
    parser.add_argument(
        "--lint",
        action="store_true",
        help="Run flake8 on src and tests if it is available in the environment.",
    )
    return parser.parse_args()


def run_quality_gates() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[2]
    test_targets = list(args.targets)

    if not args.no_coverage:
        pytest_command = build_pytest_command(test_targets, args.coverage_threshold)
        exit_code = run_command(pytest_command, repo_root)
        if exit_code != 0:
            return exit_code
    else:
        pytest_command = [
            sys.executable,
            "-m",
            "pytest",
            *test_targets,
            "-q",
            "--maxfail=1",
            "--strict-markers",
            "--strict-config",
        ]
        exit_code = run_command(pytest_command, repo_root)
        if exit_code != 0:
            return exit_code

    if args.lint:
        flake8 = [sys.executable, "-m", "flake8", "src", "tests"]
        lint_exit = run_command(flake8, repo_root)
        if lint_exit != 0:
            return lint_exit

    return 0


if __name__ == "__main__":
    raise SystemExit(run_quality_gates())
