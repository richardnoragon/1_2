#!/usr/bin/env python3
"""
Test script to verify what's happening with integration
"""

import sys
from PyQt5.QtWidgets import QApplication

def test_integration():
    # Test the import of functional integration
    try:
        from pdf_functional_integration import integrate_functional_pdf_operations, PDF_COMPONENTS_AVAILABLE
        print(f"PDF_COMPONENTS_AVAILABLE: {PDF_COMPONENTS_AVAILABLE}")
        
        if PDF_COMPONENTS_AVAILABLE:
            print("✓ All PDF components available for integration")
        else:
            print("✗ PDF components missing - integration will fail")
        
        # Test creating the widget
        app = QApplication(sys.argv)
        from enhanced_pdf_tools_widget import EnhancedPDFToolsWidget
        
        widget = EnhancedPDFToolsWidget()
        
        # Check the status after initialization
        status_text = widget.status_label.text()
        print(f"Widget status after init: {status_text}")
        
        # Check if integration was successful
        if hasattr(widget, '_pdf_integration'):
            print("✓ Integration object created")
            
            # Check if methods were replaced
            original_method = widget.__class__._encrypt_pdf_impl
            current_method = widget._encrypt_pdf_impl
            
            if original_method != current_method:
                print("✓ _encrypt_pdf_impl method was replaced")
            else:
                print("✗ _encrypt_pdf_impl method NOT replaced")
                
        else:
            print("✗ Integration object NOT created")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_integration()
