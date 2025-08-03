"""Backward compatibility module for log management functionality."""
from core.logging_manager import LogManager

# Re-export the names that were previously in this module
__all__ = ['LogManager', 'LogManagerGUI']

# Import GUI components only when needed
def get_log_viewer():
    """getlogviewer."""
    from gui.log_viewer import LogViewerWindow
    return LogViewerWindow

# Alias for backward compatibility
LogManagerGUI = get_log_viewer()

if __name__ == '__main__':
    from gui.log_viewer import main
    main()
