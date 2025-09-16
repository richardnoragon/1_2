#!/usr/bin/env python3
"""
Simple test script to verify all tools are properly integrated after organization
"""

import os
import sys


def test_imports():
    """Test that all main utilities can be imported"""
    print("Testing imports...")
    
    try:
        from src.tools import analysis
        print("✓ Analysis tools imported successfully")
    except ImportError as e:
        print(f"✗ Analysis import failed: {e}")
    
    try:
        from src.tools import security
        print("✓ Security tools imported successfully")  
    except ImportError as e:
        print(f"✗ Security import failed: {e}")
    
    try:
        from src.tools import system
        print("✓ System tools imported successfully")
    except ImportError as e:
        print(f"✗ System import failed: {e}")
    
    try:
        from src.tools import file_operations
        print("✓ File operations imported successfully")
    except ImportError as e:
        print(f"✗ File operations import failed: {e}")
        
    print("Import test completed!")

if __name__ == "__main__":
    print("=== Final Integration Test ===")
    test_imports()
    print("=== Test Complete ===")
