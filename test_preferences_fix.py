#!/usr/bin/env python3
"""
Test script to verify the Preferences integration fix.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QDialog


def test_preferences_integration():
    """Test that preferences integration works correctly."""
    print("Testing Preferences Integration Fix...")
    
    app = QApplication(sys.argv)
    
    try:
        # Import the multi-pane explorer
        from src.file_explorer.multi_pane_explorer_repaired import (
            SETTINGS_DIALOG_AVAILABLE, MultiPaneFileExplorer, SettingsDialog)
        
        print(f"✓ Multi-pane explorer imported successfully")
        print(f"Settings Dialog Available: {SETTINGS_DIALOG_AVAILABLE}")
        print(f"SettingsDialog is not None: {SettingsDialog is not None}")
        
        if SETTINGS_DIALOG_AVAILABLE and SettingsDialog:
            # Test creating a settings dialog
            settings_dialog = SettingsDialog()
            print(f"✓ SettingsDialog created: {settings_dialog.windowTitle()}")
            
            # Test creating the explorer
            explorer = MultiPaneFileExplorer()
            print("✓ MultiPaneFileExplorer created successfully")
            
            # Check if the preferences method exists and works
            if hasattr(explorer, 'open_preferences'):
                print("✓ open_preferences method exists")
                
                # Show the explorer window
                explorer.show()
                print("✓ Explorer window shown")
                
                # Test opening preferences after a short delay
                def test_open_preferences():
                    try:
                        print("Testing open_preferences method...")
                        # This should open the dialog
                        explorer.open_preferences()
                        print("✓ Preferences dialog opened successfully!")
                    except Exception as e:
                        print(f"✗ Error opening preferences: {e}")
                    finally:
                        # Close the application after test
                        QTimer.singleShot(2000, app.quit)
                
                # Schedule the test
                QTimer.singleShot(1000, test_open_preferences)
                
                print("\nWaiting for preferences test...")
                print("This will open the multi-pane explorer and then the preferences dialog.")
                print("The test will close automatically after a few seconds.")
                
                return app.exec_()
            else:
                print("✗ open_preferences method not found")
                return 1
        else:
            print("✗ SettingsDialog not available")
            return 1
            
    except Exception as e:
        print(f"✗ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = test_preferences_integration()
    sys.exit(exit_code)