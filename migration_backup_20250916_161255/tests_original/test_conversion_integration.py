#!/usr/bin/env python3
"""
Test script to verify PDF conversion functionality integration
"""

import sys
import os
from PyQt5.QtWidgets import QApplication

def test_conversion_integration():
    """Test that conversion methods are properly integrated"""
    try:
        print("Testing PDF conversion integration...")
        
        # Import the functional integration
        from pdf_functional_integration import PDFFunctionalIntegration
        print("✓ Successfully imported PDFFunctionalIntegration")
        
        # Create a mock parent widget
        app = QApplication([])
        
        class MockParentWidget:
            def __init__(self):
                self.state_manager = MockStateManager()
        
        class MockStateManager:
            def get_current_file(self):
                return None
        
        mock_parent = MockParentWidget()
        
        # Create integration instance
        integration = PDFFunctionalIntegration(mock_parent)
        print("✓ Successfully created PDFFunctionalIntegration instance")
        
        # Test that conversion methods exist
        conversion_methods = [
            'convert_to_docx_functional',
            'convert_to_image_functional', 
            'convert_html_to_pdf_functional'
        ]
        
        for method_name in conversion_methods:
            if hasattr(integration, method_name):
                print(f"✓ Found method: {method_name}")
            else:
                print(f"✗ Missing method: {method_name}")
                return False
        
        # Test that fallback methods exist
        fallback_methods = [
            '_convert_to_docx_fallback',
            '_convert_to_image_fallback'
        ]
        
        for method_name in fallback_methods:
            if hasattr(integration, method_name):
                print(f"✓ Found fallback method: {method_name}")
            else:
                print(f"✗ Missing fallback method: {method_name}")
                return False
        
        print("\n✓ All conversion functionality properly integrated!")
        return True
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_conversion_integration()
    sys.exit(0 if success else 1)
