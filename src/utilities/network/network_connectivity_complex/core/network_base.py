"""Legacy ``utilities`` shim for network connectivity base classes."""

import sys
from importlib import import_module

_SHIM_PATH = "network_org.network_connectivity_complex.core.network_base"
_SHIM = import_module(_SHIM_PATH)

setattr(
    _SHIM,
    "UTILITIES_NETWORK_SHIM_NOTICE",
    "utilities.network.* routes through network_org.* (src.tools.*).",
)

sys.modules[__name__] = _SHIM
