#!/usr/bin/env python3
"""
Software Maintenance - Entry point for the Software Maintenance Toolkit.

This module provides access to the comprehensive Software Maintenance Toolkit
including the Software Updater and De-Installer with advanced automation,
safety features, and seamless integration with the main system hub.
"""

try:
    from .software_maintenance.gui.maintenance_hub import (
        SoftwareMaintenanceHub as SoftwareMaintenanceGUI,
    )
except ImportError:
    # Fallback for different import paths
    try:
        from software_maintenance.gui.maintenance_hub import (
            SoftwareMaintenanceHub as SoftwareMaintenanceGUI,
        )
    except ImportError:
        # Final fallback - create a placeholder class
        from PyQt5.QtWidgets import (
            QMainWindow,
            QLabel,
            QVBoxLayout,
            QWidget,
            QMessageBox,
        )

        class SoftwareMaintenanceGUI(QMainWindow):
            """Placeholder class when toolkit is not available."""

            def __init__(self):
                super().__init__()
                self.setWindowTitle("Software Maintenance - Not Available")
                self.setGeometry(100, 100, 600, 400)

                central_widget = QWidget()
                self.setCentralWidget(central_widget)
                layout = QVBoxLayout(central_widget)

                label = QLabel(
                    "Software Maintenance Toolkit is not available.\n\n"
                    "Please ensure all dependencies are installed."
                )
                label.setWordWrap(True)
                layout.addWidget(label)

                # Show error message
                QMessageBox.warning(
                    self,
                    "Software Maintenance Toolkit",
                    "The Software Maintenance Toolkit could not be loaded.\n\n"
                    "Please check that all required dependencies are "
                    "installed:\n"
                    "• PyQt5\n"
                    "• Software maintenance modules\n\n"
                    "The toolkit provides:\n"
                    "• Intelligent Software Updater\n"
                    "• Powerful Software De-Installer\n"
                    "• Comprehensive backup and restore capabilities",
                )


def main():
    """Main function for standalone execution."""
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = SoftwareMaintenanceGUI()
    window.setWindowTitle(
        "Software Maintenance Toolkit - Richard's File Utilities"
    )
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
