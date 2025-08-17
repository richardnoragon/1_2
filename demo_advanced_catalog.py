#!/usr/bin/env python3
"""Demo script for the Advanced File Catalog Generator.

This script demonstrates the GUI functionality of the advanced catalog generator.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Run the Advanced File Catalog Generator demo."""
    try:
        from PyQt5.QtWidgets import QApplication
        from src.rfu.tools.file_management.advanced_catalog.advanced_catalog_window import AdvancedCatalogWindow
        
        print("Starting Advanced File Catalog Generator...")
        
        # Create QApplication
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        
        # Create and show the window
        window = AdvancedCatalogWindow()
        window.show()
        
        print("Advanced File Catalog Generator is now running!")
        print("Features available:")
        print("- Multi-criteria sorting (alphabetical, size, type, dates)")
        print("- Dynamic color-coding with accessibility support")
        print("- Real-time preview with color legend")
        print("- Export to HTML, CSV, and JSON formats")
        print("- Comprehensive file statistics")
        print("\nTo test:")
        print("1. Click 'Select Directory' to choose a folder")
        print("2. Choose sorting criteria and color scheme")
        print("3. Preview the color-coded results")
        print("4. Export to your preferred format")
        
        # Run the application
        sys.exit(app.exec_())
        
    except ImportError as e:
        print(f"Error: Could not import required modules: {e}")
        print("Make sure PyQt5 is installed: pip install PyQt5")
        return 1
    except Exception as e:
        print(f"Error starting application: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())