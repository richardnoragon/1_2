#!/usr/bin/env python3
"""Compatibility wrapper for relocated System Cleanup module."""

from src.tools.system.system_cleanup import system_cleanup as _system_cleanup

SystemCleanupGUI = _system_cleanup.SystemCleanupGUI
main = _system_cleanup.main

__all__ = ["SystemCleanupGUI", "main"]


def __getattr__(name):
    """Proxy attribute access to the relocated implementation."""
    return getattr(_system_cleanup, name)


if __name__ == "__main__":
    main()
