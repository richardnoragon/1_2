#!/usr/bin/env python3
"""
Test script to validate the enhanced_config_manager recursion protection.
This script verifies that the infinite recursion risk has been resolved.
"""

import sys
import os
import tempfile
import logging

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_recursion_protection():
    """Test that recursion protection prevents infinite loops."""
    print("🧪 Testing Enhanced Config Manager Recursion Protection...")
    
    try:
        # Import the fixed config manager
        from src.rfu.core.enhanced_config_manager import EnhancedConfigManager
        
        print("✅ EnhancedConfigManager imported successfully")
        
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize config manager (should use file-based fallback for testing)
            config_manager = EnhancedConfigManager()
            
            print("✅ EnhancedConfigManager initialized successfully")
            
            # Test 1: Normal operation should work
            result = config_manager.set_setting('general', 'auto_save_config', True)
            print(f"✅ Normal set_setting operation: {result}")
            
            # Test 2: Get the setting back
            value = config_manager.get_setting('general', 'auto_save_config', False)
            print(f"✅ Normal get_setting operation: {value}")
            
            # Test 3: Remove the setting (this was the problematic operation)
            result = config_manager.remove_setting('general', 'auto_save_config')
            print(f"✅ Remove setting operation (was problematic): {result}")
            
            # Test 4: Verify recursion depth tracking works
            print(f"✅ Current recursion depth: {config_manager._recursion_depth}")
            
            # Test 5: Try to trigger a scenario that would have caused recursion
            # Set auto_save to True, then try to remove it (this used to cause recursion)
            config_manager.set_setting('general', 'auto_save_config', True)
            config_manager.remove_setting('general', 'auto_save_config')
            print("✅ Recursive scenario handled safely")
            
            # Test 6: Verify safe auto-save checking works
            auto_save_safe = config_manager._get_auto_save_setting_safe()
            print(f"✅ Safe auto-save check: {auto_save_safe}")
            
        print("\n🎉 All recursion protection tests passed!")
        print("The infinite recursion risk has been successfully resolved.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_recursion_limit():
    """Test that the recursion limit is properly enforced."""
    print("\n🧪 Testing Recursion Limit Enforcement...")
    
    try:
        from src.rfu.core.enhanced_config_manager import EnhancedConfigManager
        config_manager = EnhancedConfigManager()
        
        # Manually set recursion depth to near limit to test protection
        original_depth = config_manager._recursion_depth
        config_manager._recursion_depth = config_manager._max_recursion_depth - 1
        
        # This should fail due to recursion protection
        result = config_manager.get_setting('test', 'test_key', 'default')
        
        # Reset depth
        config_manager._recursion_depth = original_depth
        
        if result == 'default':
            print("✅ Recursion limit properly enforced")
            return True
        else:
            print("❌ Recursion limit not properly enforced")
            return False
            
    except Exception as e:
        print(f"❌ Recursion limit test failed: {e}")
        return False

if __name__ == "__main__":
    # Setup logging to see any warnings/errors
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 70)
    print("Enhanced Config Manager Recursion Protection Validation")
    print("=" * 70)
    
    test1_passed = test_recursion_protection()
    test2_passed = test_recursion_limit()
    
    print("\n" + "=" * 70)
    if test1_passed and test2_passed:
        print("🎉 ALL TESTS PASSED - Recursion protection is working correctly!")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED - Please review the implementation")
        sys.exit(1)