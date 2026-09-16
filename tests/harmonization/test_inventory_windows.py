"""Launch every matrix entry in isolation; this is not full action coverage."""
import json
import os
from pathlib import Path
import subprocess
import sys
import pytest

ROOT = Path(__file__).resolve().parents[2]
TOOLS = json.loads((ROOT / 'docs/tool-capability-matrix.json').read_text())['tools']

@pytest.mark.parametrize('tool_id', [row['id'] for row in TOOLS])
def test_inventory_window_launch_health_and_visibility(tool_id, tmp_path):
    result = subprocess.run(
        [sys.executable, str(ROOT / 'scripts/quality/smoke_tool_inventory.py'), tool_id, str(tmp_path)],
        cwd=ROOT, capture_output=True, text=True, timeout=30,
        env={**os.environ, 'PYTHONPATH': str(ROOT)},
    )
    assert result.returncode == 0, result.stdout + result.stderr
    lines = [line for line in result.stdout.splitlines() if line.startswith('RFU_SMOKE_RESULT ')]
    assert lines, result.stdout + result.stderr
    evidence = json.loads(lines[-1].split(' ', 1)[1])
    assert evidence == {'id': tool_id, 'launch': True, 'healthy': True, 'visible': True, 'fallback_retains_state': True, 'retry_validated': True, 'return_to_hub': True}
