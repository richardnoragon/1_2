"""network_org shim module that aliases the modern network connectivity code."""

import sys
from importlib import import_module

from src.core.error_handler import error_handler as _core_error_handler

_IMPL_PATH = "src.tools.network.network_connectivity_complex.core.network_base"
_IMPL = import_module(_IMPL_PATH)

if not hasattr(_IMPL, "error_handler"):
    setattr(_IMPL, "error_handler", _core_error_handler)

setattr(
    _IMPL,
    "NETWORK_ORG_SHIM_NOTICE",
    "network_org is a compatibility shim; prefer src.tools.network.*",
)

setattr(_IMPL, "NETWORK_ORG_SHIM_TARGET", _IMPL_PATH)

sys.modules[__name__] = _IMPL
