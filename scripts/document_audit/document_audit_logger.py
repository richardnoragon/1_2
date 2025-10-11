#!/usr/bin/env python3
"""Generate SHA-256 audit trail entries for documentation artifacts."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCOPE = REPO_ROOT / "docs" / "enterprise_documentation"
DEFAULT_OUTPUT = (
    REPO_ROOT / "reports" / "audit_trail" / "section_1_1_document_audit_log.csv"
)


def _iso_now() -> str:
    return (
        dt.datetime.now(dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _should_skip(path: Path) -> bool:
    return any(part.startswith(".") for part in path.parts)


def _iter_files(scope: Path) -> Iterable[Path]:
    target = scope if scope.is_absolute() else (REPO_ROOT / scope)
    target = target.resolve()
    if not target.exists():
        raise FileNotFoundError(f"Scope path not found: {scope}")
    if target.is_file():
        if _should_skip(target):
            return []
        return [target]
    files: list[Path] = []
    for candidate in sorted(target.rglob("*")):
        if candidate.is_file() and not _should_skip(candidate):
            files.append(candidate)
    return files


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def log_audit(scope: Path, output: Path, operator: str) -> None:
    files = _iter_files(scope)
    output.parent.mkdir(parents=True, exist_ok=True)
    is_new = not output.exists()
    with output.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        if is_new:
            writer.writerow(
                [
                    "timestamp_utc",
                    "artifact_path",
                    "sha256",
                    "change_type",
                    "operator",
                ]
            )
        timestamp = _iso_now()
        for file_path in files:
            relative = file_path.relative_to(REPO_ROOT)
            writer.writerow(
                [
                    timestamp,
                    str(relative),
                    _sha256(file_path),
                    "verification",
                    operator,
                ]
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Log SHA-256 hashes for documentation artifacts."
    )
    parser.add_argument(
        "--scope",
        type=Path,
        default=DEFAULT_SCOPE,
        help="File or directory to hash",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Audit CSV output file",
    )
    parser.add_argument(
        "--operator",
        default="automation",
        help="Operator identifier for the audit record",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    log_audit(args.scope, args.output, args.operator)
    print(f"Audit trail updated: {args.output}")


if __name__ == "__main__":
    main()
