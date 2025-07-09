"""Backward compatibility module for configuration management functionality."""

from core.config_manager import ConfigManager
from gui.settings_dialog import SettingsDialog

# Re-export the names that were previously in this module
__all__ = ['ConfigManager', 'SettingsDialog']

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = SettingsDialog()
    dialog.show()
    sys.exit(app.exec_())
