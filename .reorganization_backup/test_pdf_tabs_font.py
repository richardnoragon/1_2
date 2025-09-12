#!/usr/bin/env python3
"""
Test script to view the PDF Tools tab font changes
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from enhanced_pdf_tools_widget import EnhancedPDFToolsWidget

def main():
    """Test the PDF tools widget with updated fonts"""
    app = QApplication(sys.argv)
    
    # Create test window
    window = QMainWindow()
    window.setWindowTitle("PDF Tools - Font Test")
    window.setGeometry(200, 200, 1000, 800)
    
    # Create and set the PDF tools widget
    pdf_widget = EnhancedPDFToolsWidget()
    window.setCentralWidget(pdf_widget)
    
    # Show the window
    window.show()
    
    print("PDF Tools widget loaded with updated tab fonts:")
    print("- Font weight: Changed from bold to normal")
    print("- Font size: Changed from 12pt to 11pt") 
    print("- Text color: Added explicit color (#495057)")
    print("- Selected tab: Bold font weight for active tab")
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
