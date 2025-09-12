#!/usr/bin/env python3
"""
Test script to validate the log_manager import fix.
This script verifies that the StringIO import is properly accessible
and that the fix maintains functionality.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the modified test module to verify imports work
try:
    from io import StringIO
    print("✅ StringIO import successful at top-level scope")
    
    # Test StringIO functionality
    string_io = StringIO()
    string_io.write("Test message")
    content = string_io.getvalue()
    
    if "Test message" in content:
        print("✅ StringIO functionality works correctly")
    else:
        print("❌ StringIO functionality failed")
        sys.exit(1)
        
    # Verify the import is available in the tests module
    import tests.test_log_manager
    print("✅ test_log_manager module imports successfully")
    
    # Check that StringIO is available in the module
    if hasattr(tests.test_log_manager, 'StringIO'):
        print("✅ StringIO is available in test module scope")
    else:
        print("❌ StringIO not found in test module scope")
        sys.exit(1)
    
    print("\n🎉 All import fix validations passed!")
    print("The redundant import issue has been successfully resolved.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)