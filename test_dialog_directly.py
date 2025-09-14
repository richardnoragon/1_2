#!/usr/bin/env python3
"""Direct test of the startup dialog to check radio button text visibility."""

import os
import sys

from PyQt5.QtWidgets import QApplication, QMessageBox


def test_startup_dialog():
    """Test the startup dialog directly."""
    app = QApplication(sys.argv)
    
    try:
        # Import the startup dialog class directly
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from main import InterfaceSelectionDialog

        # Create the dialog
        dialog = InterfaceSelectionDialog()
        print("Dialog object created successfully")
        
        # Actually show the dialog (this creates the UI elements)
        print("Showing dialog...")
        result = dialog.show_selection_dialog()
        print(f"Dialog result: {result}")
        
        # Check if radio buttons exist and have text after dialog is shown
        if hasattr(dialog, 'dialog_radio') and dialog.dialog_radio is not None:
            dialog_text = dialog.dialog_radio.text()
            print(f"Dialog radio text: '{dialog_text}'")
            
            if hasattr(dialog, 'pane_radio') and dialog.pane_radio is not None:
                pane_text = dialog.pane_radio.text()
                print(f"Pane radio text: '{pane_text}'")
                
                if dialog_text and pane_text:
                    print("✅ Radio button texts are present!")
                    print("Dialog completed successfully")
                else:
                    print("❌ Radio button texts are empty!")
            else:
                print("❌ Pane radio button not found!")
        else:
            print("❌ Dialog radio button not found!")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    app.quit()

if __name__ == "__main__":
    test_startup_dialog()