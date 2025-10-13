"""Richard's File Utilities - Network Tools"""

# Import simplified network tools directly
try:
    from .connectivity import NetworkConnectivityGUI
except ImportError as e:
    print(f"Warning: Could not import NetworkConnectivityGUI: {e}")
    NetworkConnectivityGUI = None

try:
    from .scanner.network_scanner import NetworkScannerGUI
except ImportError as e:
    print(f"Warning: Could not import NetworkScannerGUI: {e}")
    NetworkScannerGUI = None

try:
    from .transfer.network_transfer import NetworkTransferGUI
except ImportError as e:
    print(f"Warning: Could not import NetworkTransferGUI: {e}")
    NetworkTransferGUI = None

__all__ = []
if NetworkConnectivityGUI:
    __all__.append("NetworkConnectivityGUI")
if NetworkScannerGUI:
    __all__.append("NetworkScannerGUI")
if NetworkTransferGUI:
    __all__.append("NetworkTransferGUI")
