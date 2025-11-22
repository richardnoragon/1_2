"""Legacy ``utilities`` namespace shim.

The historical File Utilities codebase used ``utilities.*`` imports. The new
architecture lives under ``src.tools.*``; this package re-exports only the
pieces that still have outstanding tests so the migration can finish without
breaking pytest.
"""

from . import network

__all__ = ["network"]
