"""Automation for Roadmap Section 1.1 repository footprint status reporting."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set

CANONICAL_LAUNCHER_KEY = "src/main.py"
CANONICAL_LAUNCHER_PATH = Path("src") / "main.py"
ROOT_LAUNCHER_KEY = "main.py"
ROOT_LAUNCHER_PATH = Path("main.py")
RETIRED_LAUNCHER_KEY = "src/rfu/main.py"
RETIRED_LAUNCHER_PATH = Path("src") / "rfu" / "main.py"


@dataclass
class CheckResult:
    """Represents the outcome of a validation check."""

    name: str
    status: str
    details: Dict[str, List[str]]
    notes: List[str]


def _get_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _list_top_level_directories(root: Path) -> Set[str]:
    return {item.name for item in root.iterdir() if item.is_dir()}


def _validate_top_level_directories(root: Path) -> CheckResult:
    expected = {
        "src",
        "tests",
        "docs",
        "scripts",
        "config",
        "core",
        "resources",
        "reports",
        "assets",
        "logs",
        "results",
        "rfu_reports",
        "RFU_Hub_Preferences_Security_Implementation_Plan",
        "archive",
        "backups",
        "src_backup",
        "emergency-backup-20250925_200754",
        ".benchmarks",
        ".roo",
        ".specify",
        ".vscode",
    }
    actual = _list_top_level_directories(root)

    missing = sorted(expected - actual)
    unexpected = sorted(
        name for name in actual - expected if not name.startswith(".git")
    )

    status = "complete" if not missing else "attention"
    notes: List[str] = []
    if unexpected:
        notes.append(
            "Additional directories detected; review change log "
            "for required updates."
        )
    if missing:
        notes.append(
            "One or more expected directories are missing from the repository."
        )

    details = {
        "expected_present": sorted(expected & actual),
        "missing": missing,
        "unexpected": unexpected,
    }
    return CheckResult(
        name="top_level_directories",
        status=status,
        details=details,
        notes=notes,
    )


def _validate_legacy_locations(root: Path) -> CheckResult:
    legacy_items = {
        "src_backup": root / "src_backup",
        "archive": root / "archive",
        "RFU_Hub_Preferences_Security_Implementation_Plan": root
        / "RFU_Hub_Preferences_Security_Implementation_Plan",
    }
    absent_files = []
    for name, path in legacy_items.items():
        if not path.exists():
            absent_files.append(name)

    main_backup = root / "main.py.backup"
    unexpected_files = []
    if main_backup.exists():
        unexpected_files.append(str(main_backup))

    status = "complete"
    if absent_files or unexpected_files:
        status = "attention"
    notes = []
    if absent_files:
        notes.append("Expected legacy locations missing; confirm archival process.")
    if unexpected_files:
        notes.append(
            "Unexpected legacy file(s) present; remove or document " "remediation plan."
        )

    details = {
        "legacy_locations_present": sorted(legacy_items.keys() - set(absent_files)),
        "legacy_locations_missing": absent_files,
        "unexpected_legacy_files": unexpected_files,
    }
    return CheckResult(
        name="legacy_code_locations",
        status=status,
        details=details,
        notes=notes,
    )


def _validate_gui_entry_points(root: Path) -> CheckResult:
    expected = {
        "src/main.py": root / "src" / "main.py",
        "main.py": root / "main.py",
        "rfu_explorer.py": root / "rfu_explorer.py",
        "demo_pyvisualizer.py": root / "demo_pyvisualizer.py",
        "simple_pyvisualizer_demo.py": root / "simple_pyvisualizer_demo.py",
    }
    retired = {
        "src/rfu/main.py": root / "src" / "rfu" / "main.py",
    }

    missing = sorted(name for name, path in expected.items() if not path.exists())

    status = "complete" if not missing else "attention"
    notes = []
    if missing:
        notes.append("One or more GUI entry points are missing; investigate promptly.")

    retired_present = sorted(name for name, path in retired.items() if path.exists())
    if retired_present:
        notes.append(
            "Retired launcher paths detected; plan cleanup when safe to do so."
        )

    details = {
        "expected_present": sorted(set(expected.keys()) - set(missing)),
        "missing": missing,
        "retired_present": retired_present,
    }
    return CheckResult(
        name="gui_entry_points",
        status=status,
        details=details,
        notes=notes,
    )


def _validate_configuration_artifacts(root: Path) -> CheckResult:
    expected_files = {
        "config/rfu_config.json": root / "config" / "rfu_config.json",
        ".env": root / ".env",
    }
    expected_directories = {
        "reports": root / "reports",
        "results": root / "results",
        ".mypy_cache": root / ".mypy_cache",
        ".pytest_cache": root / ".pytest_cache",
    }

    missing = []
    for name, path in expected_files.items():
        if not path.exists():
            missing.append(name)
    for name, path in expected_directories.items():
        if not path.exists():
            missing.append(name)

    status = "complete" if not missing else "attention"
    notes = []
    if missing:
        notes.append("Configuration artifacts missing; ensure environment parity.")

    details = {
        "expected_present": sorted(
            set(expected_files.keys()).union(expected_directories.keys()) - set(missing)
        ),
        "missing": sorted(missing),
    }
    return CheckResult(
        name="configuration_artifacts",
        status=status,
        details=details,
        notes=notes,
    )


def _write_status_report(root: Path, results: List[CheckResult]) -> Path:
    output_dir = root / "reports" / "status_reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "roadmap_section_1_1_status.json"

    payload = {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "checks": [asdict(result) for result in results],
        "overall_status": (
            "complete"
            if all(result.status == "complete" for result in results)
            else "attention"
        ),
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path


def main() -> None:
    repo_root = _get_repo_root()
    results = [
        _validate_top_level_directories(repo_root),
        _validate_legacy_locations(repo_root),
        _validate_gui_entry_points(repo_root),
        _validate_configuration_artifacts(repo_root),
    ]
    output_path = _write_status_report(repo_root, results)

    print("Section 1.1 repository footprint status report generated.")
    print(f"Output: {output_path}")
    for result in results:
        print(f"- {result.name}: {result.status}")
        if result.notes:
            for note in result.notes:
                print(f"  NOTE: {note}")


if __name__ == "__main__":
    main()
