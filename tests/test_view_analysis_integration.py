#!/usr/bin/env python3
"""
Test script to verify PDF viewer and miner functionality integration
"""

import sys
import os
from PyQt5.QtWidgets import QApplication

def test_view_analysis_integration():
    """Test that PDF viewer and miner methods are properly integrated"""
    try:
        print("Testing PDF viewer and miner integration...")
        
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
        
        # Test that view and analysis methods exist
        view_analysis_methods = [
            'view_pdf_functional',
            'analyze_pdf_functional'
        ]
        
        for method_name in view_analysis_methods:
            if hasattr(integration, method_name):
                print(f"✓ Found method: {method_name}")
            else:
                print(f"✗ Missing method: {method_name}")
                return False
        
        # Test that fallback methods exist
        fallback_methods = [
            '_view_pdf_fallback',
            '_analyze_pdf_fallback',
            '_show_analysis_results'
        ]
        
        for method_name in fallback_methods:
            if hasattr(integration, method_name):
                print(f"✓ Found fallback method: {method_name}")
            else:
                print(f"✗ Missing fallback method: {method_name}")
                return False
        
        print("\n✓ All PDF viewer and miner functionality properly integrated!")
        return True
        
    except Exception as e:
        print(f"✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_view_analysis_integration()
    sys.exit(0 if success else 1)
