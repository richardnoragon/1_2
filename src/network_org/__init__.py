"""Compatibility namespace for legacy network connectivity imports.

This package re-exports modern RFU network modules so historical paths
(such as ``utilities.network``) keep working while the remaining tests
are migrated. New code should import from ``src.tools.network`` directly.
"""

SHIM_NOTICE = (
    "network_org is a shim namespace. It only exists to keep legacy\n"
    "network connectivity imports alive while the suites move to the\n"
    "modern src.tools.* packages."
)

__all__ = ["SHIM_NOTICE"]
