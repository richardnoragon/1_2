#!/usr/bin/env python3
"""
Test script to demonstrate the improved PDF Tools tab layout
with optimized font size and shortened tab names
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from enhanced_pdf_tools_widget import EnhancedPDFToolsWidget

def main():
    """Test the PDF tools widget with improved tab layout"""
    app = QApplication(sys.argv)
    
    # Create test window
    window = QMainWindow()
    window.setWindowTitle("PDF Tools - Improved Tab Layout Test")
    window.setGeometry(200, 200, 1200, 900)
    
    # Create main widget with instructions
    main_widget = QWidget()
    layout = QVBoxLayout(main_widget)
    
    # Add header with improvements info
    info_label = QLabel("""
<h2>PDF Tools - Tab Layout Improvements</h2>
<p><b>Changes Made:</b></p>
<ul>
<li>Font size reduced from 11pt to 9pt for better fit</li>
<li>Tab names shortened for clarity: Operations, Extract, Security, Enhance, Convert, View & Analyze</li>
<li>Added min-width (80px) and max-width (140px) constraints</li>
<li>Enabled scroll buttons if tabs don't fit</li>
<li>Reduced padding and margins for better space utilization</li>
</ul>
<p><b>Result:</b> All tab text should now be fully visible without truncation.</p>
    """)
    info_label.setWordWrap(True)
    info_label.setStyleSheet("""
        QLabel {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 15px;
            margin: 10px;
        }
    """)
    layout.addWidget(info_label)
    
    # Create and add the PDF tools widget
    pdf_widget = EnhancedPDFToolsWidget()
    layout.addWidget(pdf_widget)
    
    window.setCentralWidget(main_widget)
    
    # Show the window
    window.show()
    
    print("PDF Tools widget loaded with improved tab layout:")
    print("✓ Smaller font size (9pt) for better fit")
    print("✓ Shortened tab names for clarity")
    print("✓ Width constraints to prevent overflow")
    print("✓ Scroll buttons enabled if needed")
    print("✓ All text should be fully visible now")
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
