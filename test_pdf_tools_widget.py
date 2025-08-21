#!/usr/bin/env python3
"""
Test script to demonstrate the new PDF Tools Widget functionality
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

try:
    from src.rfu.tools.pdf.widgets.enhanced_pdf_tools_widget import EnhancedPDFToolsWidget
    
    class TestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("PDF Tools Widget Test - Folder-Based Structure")
            self.setGeometry(200, 200, 1200, 800)
            
            # Create central widget
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Create layout
            layout = QVBoxLayout(central_widget)
            
            # Add the PDF tools widget
            self.pdf_widget = EnhancedPDFToolsWidget(self)
            layout.addWidget(self.pdf_widget)
            
            self.show()
    
    if __name__ == "__main__":
        app = QApplication(sys.argv)
        
        print("Testing PDF Tools Widget with folder-based structure...")
        print("Expected behavior:")
        print("1. Shows category buttons based on actual folder structure:")
        print("   - Basic Operations (merge, split, sign)")
        print("   - Content Extraction (extract text, images, tables, etc.)")
        print("   - Security (encrypt)")
        print("   - Enhancements")
        print("   - Conversion")
        print("   - View & Analysis")
        print("2. When you click a category, it shows the actual programs in that folder")
        print("3. You can click 'Back to Categories' to return to the main view")
        print()
        
        window = TestWindow()
        
        # Check if PDF tools folders exist
        pdf_tools_path = project_root / "src" / "utilities" / "pdf_tools"
        if pdf_tools_path.exists():
            print(f"PDF Tools folder found at: {pdf_tools_path}")
            for folder in pdf_tools_path.iterdir():
                if folder.is_dir() and folder.name.startswith('pdf_'):
                    files = list(folder.glob("*.py"))
                    py_files = [f.name for f in files if f.name != '__init__.py']
                    print(f"  {folder.name}: {len(py_files)} programs - {py_files}")
        else:
            print(f"PDF Tools folder not found at: {pdf_tools_path}")
        
        sys.exit(app.exec_())
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the project root directory")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()