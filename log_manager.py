"""Backward compatibility module for log management functionality."""
from core.logging_manager import LogManager
from gui.log_viewer import LogViewerWindow, main

# Re-export the names that were previously in this module
__all__ = ['LogManager', 'LogManagerGUI', 'main']

# Alias for backward compatibility
LogManagerGUI = LogViewerWindow
    
if __name__ == '__main__':
    main()





if __name__ == '__main__':
    main()
