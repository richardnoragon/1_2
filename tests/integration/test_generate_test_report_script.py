import json
import subprocess
import sys
from pathlib import Path


def test_generate_report_handles_missing_artifacts_dir(tmp_path):
    script_path = (
        Path(__file__).resolve().parent
        / "scripts"
        / "generate_test_report.py"
    )
    artifacts_dir = tmp_path / "missing-artifacts"
    output_dir = tmp_path / "reports"

    result = subprocess.run(
        [
            sys.executable,
            str(script_path),
            "--artifacts-dir",
            str(artifacts_dir),
            "--output-dir",
            str(output_dir),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert (output_dir / "summary.json").exists()

    with open(output_dir / "summary.json", "r", encoding="utf-8") as f:
        summary = json.load(f)

    assert summary["overall_status"] == "no_tests"
