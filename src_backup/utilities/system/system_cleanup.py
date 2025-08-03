#!/usr/bin/env python3
"""
System Cleanup - Simple alias for system diagnostics tools.
"""

from .diagnostics_monitoring import SystemDiagnosticsGUI as SystemCleanupGUI


def main():
    """Main function for standalone execution."""
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = SystemCleanupGUI()
    window.setWindowTitle("System Cleanup - Richard's File Utilities")
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
