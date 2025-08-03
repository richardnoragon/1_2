#!/usr/bin/env python3
"""
Network Scanner - Simple alias for network connectivity tools.
"""

from .network_connectivity import NetworkConnectivityGUI as NetworkScannerGUI


def main():
    """Main function for standalone execution."""
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = NetworkScannerGUI()
    window.setWindowTitle("Network Scanner - Richard's File Utilities")
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
