"""
src.tools.network.transfer package
"""

try:
    from .network_transfer import NetworkTransferGUI
except ImportError as exc:  # pragma: no cover - optional import path
    print(f"Warning: Could not import NetworkTransferGUI: {exc}")
    NetworkTransferGUI = None

__all__ = []
if NetworkTransferGUI:
    __all__.append("NetworkTransferGUI")
