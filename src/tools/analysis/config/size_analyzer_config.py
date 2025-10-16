"""Compatibility shim for the relocated Size Analyzer configuration module."""

from ..size_analyzer.size_analyzer_config import (
    SizeAnalyzerConfig,
    get_config_manager,
    get_log_manager,
)

__all__ = [
    "SizeAnalyzerConfig",
    "get_config_manager",
    "get_log_manager",
]
