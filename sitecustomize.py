"""Project-wide interpreter customizations.

Currently ensures Pytest 8.x maintains backward compatibility with
``pytest-lazy-fixture`` by recreating the deprecated ``CallSpec2.funcargs``
property before plugin initialization executes. This keeps legacy fixtures
stable without requiring an immediate plugin upgrade.
"""

from __future__ import annotations

import os
from typing import Any, Dict

if os.name == "posix" and not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:  # pragma: no cover - optional dependency for pytest runs only
    from _pytest.python import CallSpec2
except Exception:  # pragma: no cover - pytest not imported/installed
    CallSpec2 = None  # type: ignore[assignment]
else:
    if not hasattr(CallSpec2, "funcargs"):

        def _get_funcargs(self: "CallSpec2") -> Dict[str, Any]:
            return getattr(self, "_lazy_fixture_funcargs", {})

        def _set_funcargs(self: "CallSpec2", value: Dict[str, Any] | None) -> None:
            setattr(self, "_lazy_fixture_funcargs", value or {})

        CallSpec2.funcargs = property(_get_funcargs, _set_funcargs)
