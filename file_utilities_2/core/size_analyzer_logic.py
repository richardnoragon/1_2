"""
Compatibility wrapper for Size Analyzer core logic.

This module preserves backwards compatibility for code that still imports
`file_utilities_2.core.size_analyzer_logic` while delegating the actual
implementation to the canonical module under `src.tools.analysis`.

The full implementation now lives in
`src.tools.analysis.size_analyzer.size_analyzer_logic`. By re-exporting the
public classes, we avoid maintaining duplicate copies of the logic and ensure
future updates automatically flow through to legacy import paths.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Tuple


def _import_size_analyzer() -> Tuple[object, object]:
    """Import SizeAnalyzer components from the canonical module.

    We prefer the `src.`-prefixed path when the repository root is on
    `sys.path` but gracefully fall back to the shorter package path for
    environments that already expose `tools` directly.
    """

    try:  # Prefer fully-qualified src path
        from src.tools.analysis.size_analyzer.size_analyzer_logic import (
            SizeAnalyzer,
            SizeAnalyzerWorker,
        )

        return SizeAnalyzer, SizeAnalyzerWorker
    except ImportError:
        from tools.analysis.size_analyzer.size_analyzer_logic import (
            SizeAnalyzer,
            SizeAnalyzerWorker,
        )

        return SizeAnalyzer, SizeAnalyzerWorker


SizeAnalyzer, SizeAnalyzerWorker = _import_size_analyzer()

__all__ = ["SizeAnalyzer", "SizeAnalyzerWorker"]


if TYPE_CHECKING:
    # During static analysis expose the concrete types for improved tooling.
    from src.tools.analysis.size_analyzer.size_analyzer_logic import (
        SizeAnalyzer as _SizeAnalyzer,
        SizeAnalyzerWorker as _SizeAnalyzerWorker,
    )
