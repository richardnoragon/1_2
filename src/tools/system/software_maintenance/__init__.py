"""
Software Maintenance Toolkit for Richard's File Utilities

This module provides comprehensive software management capabilities including
an intelligent Software Updater and powerful De-Installer with advanced
automation, safety features, and seamless integration with the main system hub.

Features:
- Intelligent Software Updater with multi-source scanning
- Powerful De-Installer with deep system scanning
- Comprehensive backup and restore capabilities
- Administrative privilege management
- Real-time progress tracking and status reporting
- Seamless integration with RFU Hub
"""

__version__ = "1.0.0"
__author__ = "Richard's File Utilities"

from .core.maintenance_base import MaintenanceToolBase
from .core.security_manager import SecurityManager
from .core.software_detector import SoftwareDetector

# Import the GUI class for external access before pulling in the launcher to
# avoid circular import issues during package initialization.
try:
    from .gui.maintenance_hub import SoftwareMaintenanceHub as SoftwareMaintenanceGUI
except ImportError:
    # Fallback placeholder if GUI dependencies are missing
    from PyQt5.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget

    class SoftwareMaintenanceGUI(QMainWindow):
        """Placeholder class when GUI dependencies are missing."""

        def __init__(self):
            super().__init__()
            self.setWindowTitle("Software Maintenance - Dependencies Missing")
            self.setGeometry(100, 100, 600, 400)

            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)

            label = QLabel(
                "Software Maintenance Toolkit GUI is not available.\n\n"
                "Missing dependencies detected."
            )
            label.setWordWrap(True)
            layout.addWidget(label)


from .software_maintenance import main

__all__ = [
    "MaintenanceToolBase",
    "SoftwareDetector",
    "SecurityManager",
    "SoftwareMaintenanceGUI",
    "main",
]
