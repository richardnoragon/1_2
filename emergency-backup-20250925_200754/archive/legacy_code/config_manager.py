"""Backward compatibility module for configuration management functionality."""

from core.config_manager import ConfigManager

# Re-export the names that were previously in this module
__all__ = ['ConfigManager', 'SettingsDialog']

def get_settings_dialog():
    """Get the settings dialog class lazily to avoid circular imports."""
    from gui.settings_dialog import SettingsDialog
    return SettingsDialog

# Alias for backward compatibility
SettingsDialog = get_settings_dialog()

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = SettingsDialog()
    dialog.show()
    sys.exit(app.exec_())
