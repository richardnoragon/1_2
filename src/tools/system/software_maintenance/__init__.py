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
from src.rfu.localization import localized_widget as _ui_widget, bind_literal as _ui_bind

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
            _ui_bind(self, 'setWindowTitle', 'Legacy.sdb9acf8afed7655f')
            self.setGeometry(100, 100, 600, 400)

            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)

            label = _ui_widget(QLabel, 'Legacy.s6cd9fa36afdc305e', 'setText')
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
