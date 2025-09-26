"""Richard's File Utilities - Network Tools"""

# Import simplified network tools directly
try:
    from .network_connectivity import NetworkConnectivityGUI
except ImportError as e:
    print(f"Warning: Could not import NetworkConnectivityGUI: {e}")
    NetworkConnectivityGUI = None

try:
    from .network_scanner import NetworkScannerGUI
except ImportError as e:
    print(f"Warning: Could not import NetworkScannerGUI: {e}")
    NetworkScannerGUI = None

__all__ = []
if NetworkConnectivityGUI:
    __all__.append('NetworkConnectivityGUI')
if NetworkScannerGUI:
    __all__.append('NetworkScannerGUI')
