"""Keep import-time preference and telemetry setup away from the real database."""

import tempfile
import sys
from pathlib import Path
import pytest

from src.database.database_manager import DatabaseManager

_directory = tempfile.TemporaryDirectory(prefix="rfu-harmonization-")
DatabaseManager(Path(_directory.name) / "test.db")


@pytest.fixture(autouse=True)
def fail_on_qt_exception(monkeypatch):
    errors = []
    monkeypatch.setattr(sys, "excepthook", lambda kind, value, trace: errors.append(value))
    yield
    assert not errors, f"Unhandled Qt callback exceptions: {errors}"
