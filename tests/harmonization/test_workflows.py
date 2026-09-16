import hashlib
from threading import Event

import pytest

from src.core.workflows import inspect_files, WorkflowCancelled


def test_discovery_checksums_and_cancellation(tmp_path):
    (tmp_path / "b.txt").write_bytes(b"b")
    (tmp_path / "a.txt").write_bytes(b"a")
    progress = []
    result = inspect_files(tmp_path, progress=progress.append, emit=lambda *a, **k: None)
    assert [row.path for row in result] == ["a.txt", "b.txt"]
    assert result[0].sha256 == hashlib.sha256(b"a").hexdigest()
    assert progress == [1, 2]
    cancel = Event()
    cancel.set()
    with pytest.raises(WorkflowCancelled):
        inspect_files(tmp_path, cancel=cancel, emit=lambda *a, **k: None)
    assert (tmp_path / "a.txt").read_bytes() == b"a"


def test_symlinks_are_excluded(tmp_path):
    file = tmp_path / "original"
    file.write_bytes(b"data")
    try:
        (tmp_path / "alias").symlink_to(file)
    except OSError:
        pytest.skip("Symlinks unavailable")
    rows = inspect_files(tmp_path, emit=lambda *a, **k: None)
    assert [row.path for row in rows] == ["original"]


def test_cancelled_export_preserves_existing_report(tmp_path):
    from src.core.workflows import export_report, FileDigest
    destination = tmp_path / "report.csv"
    destination.write_text("previous report")
    cancel = Event()
    cancel.set()
    with pytest.raises(WorkflowCancelled):
        export_report([FileDigest("a", 1, "digest")], destination, cancel=cancel)
    assert destination.read_text() == "previous report"
    assert list(tmp_path.iterdir()) == [destination]


def test_export_escapes_spreadsheet_formulas(tmp_path):
    from src.core.workflows import export_report, FileDigest
    destination = tmp_path / "report.csv"
    export_report([FileDigest("=cmd", 1, "digest")], destination)
    assert "'=cmd" in destination.read_text()
