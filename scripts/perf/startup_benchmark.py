"""Quick startup benchmark for the default RFU import path.

This intentionally measures the cold import path without launching the GUI, so it
captures whether optional subsystems are still initialized at import time.
"""

from __future__ import annotations

import importlib
import sys
import time
from pathlib import Path


def benchmark_import(module_name: str = "main", trials: int = 5) -> dict[str, float]:
    """Return timing data for repeated module imports.

    The module is reloaded each pass to mimic a fresh process startup in a compact
    way without constructing the full application UI.
    """
    timings: list[float] = []
    for _ in range(trials):
        sys.modules.pop(module_name, None)
        start = time.perf_counter()
        importlib.import_module(module_name)
        elapsed = time.perf_counter() - start
        timings.append(elapsed)
    return {
        "trials": trials,
        "min_seconds": min(timings),
        "max_seconds": max(timings),
        "avg_seconds": sum(timings) / len(timings),
        "samples_ms": [round(value * 1000, 2) for value in timings],
    }


if __name__ == "__main__":
    results = benchmark_import()
    print(f"RFU startup benchmark: {results}")
