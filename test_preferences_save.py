#!/usr/bin/env python3
"""
Test script to verify the preferences save functionality.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QDialog


def test_preferences_save():
    """Test that preferences save functionality works correctly."""
    print("Testing Preferences Save Fix...")
    
    app = QApplication(sys.argv)
    
    try:
        from src.gui.settings_dialog import SettingsDialog
        
        print("✓ SettingsDialog imported successfully")
        
        # Create settings dialog
        settings_dialog = SettingsDialog()
        print("✓ SettingsDialog created successfully")
        
        # Test saving settings programmatically
        print("\nTesting save_settings method...")
        
        # Change theme to dark (this was the failing operation)
        settings_dialog.theme_combo.setCurrentText("dark")
        print("✓ Theme changed to dark")
        
        # Try to save settings
        try:
            settings_dialog.save_settings()
            print("✓ save_settings() completed without error!")
            
            # Verify the setting was saved
            saved_theme = settings_dialog.config.get_setting('general', 'theme', 'light')
            print(f"✓ Saved theme verified: {saved_theme}")
            
            if saved_theme == "dark":
                print("✅ SAVE FUNCTIONALITY IS WORKING!")
                return 0
            else:
                print("✗ Theme was not saved correctly")
                return 1
                
        except Exception as e:
            print(f"✗ save_settings() failed: {e}")
            import traceback
            traceback.print_exc()
            return 1
            
    except Exception as e:
        print(f"✗ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = test_preferences_save()
    print(f"\nTest completed with exit code: {exit_code}")
    sys.exit(exit_code)