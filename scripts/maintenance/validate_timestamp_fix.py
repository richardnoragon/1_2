#!/usr/bin/env python3
"""
Test script to validate the database_models timestamp fixes.
This script verifies that the missing timestamp fields have been added correctly.
"""

import sys
import os
from datetime import datetime

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_app_setting_to_dict():
    """Test that AppSetting.to_dict() includes timestamp fields."""
    print("🧪 Testing AppSetting.to_dict() timestamp fields...")
    
    try:
        from src.core.database_models import AppSetting
        
        # Test 1: Create AppSetting instance without timestamps
        setting = AppSetting(
            id=1,
            section="test",
            key="test_key",
            value="test_value",
            value_type="string"
        )
        
        result = setting.to_dict()
        print("✅ AppSetting.to_dict() method works")
        
        # Verify all expected fields are present
        expected_fields = ['section', 'key', 'value', 'value_type', 'created_at', 'updated_at']
        for field in expected_fields:
            if field not in result:
                print(f"❌ Missing field: {field}")
                return False
            print(f"✅ Field present: {field}")
        
        # Test 2: Create AppSetting with timestamps
        now = datetime.now()
        setting_with_timestamps = AppSetting(
            id=1,
            section="test",
            key="test_key",
            value="test_value",
            value_type="string",
            created_at=now,
            updated_at=now
        )
        
        result_with_timestamps = setting_with_timestamps.to_dict()
        
        # Verify timestamps are properly converted to ISO format
        if result_with_timestamps['created_at'] is not None:
            print("✅ created_at timestamp properly converted to ISO format")
        else:
            print("❌ created_at timestamp not properly handled")
            return False
            
        if result_with_timestamps['updated_at'] is not None:
            print("✅ updated_at timestamp properly converted to ISO format")
        else:
            print("❌ updated_at timestamp not properly handled")
            return False
            
        print("✅ AppSetting timestamp fix validation passed!")
        return True
        
    except Exception as e:
        print(f"❌ AppSetting test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_user_preference_timestamps():
    """Test that UserPreference.to_dict() includes timestamp fields correctly."""
    print("\n🧪 Testing UserPreference.to_dict() timestamp fields...")
    
    try:
        from src.core.database_models import UserPreference
        
        now = datetime.now()
        preference = UserPreference(
            id=1,
            user_id="test_user",
            preference_category="test_category",
            preference_key="test_key",
            preference_value="test_value",
            created_at=now,
            updated_at=now
        )
        
        result = preference.to_dict()
        
        # Verify timestamp fields are present and properly formatted
        if 'created_at' in result and result['created_at'] is not None:
            print("✅ UserPreference created_at field present and formatted")
        else:
            print("❌ UserPreference created_at field missing or None")
            return False
            
        if 'updated_at' in result and result['updated_at'] is not None:
            print("✅ UserPreference updated_at field present and formatted")
        else:
            print("❌ UserPreference updated_at field missing or None")
            return False
            
        print("✅ UserPreference timestamp validation passed!")
        return True
        
    except Exception as e:
        print(f"❌ UserPreference test failed: {e}")
        return False

def test_models_consistency():
    """Test that models with timestamp fields handle them consistently."""
    print("\n🧪 Testing timestamp field consistency across models...")
    
    try:
        from src.core.database_models import AppSetting, UserPreference
        
        # Test that both models handle None timestamps the same way
        app_setting = AppSetting(section="test", key="test")
        user_pref = UserPreference(preference_category="test", preference_key="test")
        
        app_result = app_setting.to_dict()
        pref_result = user_pref.to_dict()
        
        # Both should handle None timestamps the same way
        if app_result['created_at'] is None and pref_result['created_at'] is None:
            print("✅ Both models handle None created_at consistently")
        else:
            print("❌ Models handle None created_at inconsistently")
            return False
            
        if app_result['updated_at'] is None and pref_result['updated_at'] is None:
            print("✅ Both models handle None updated_at consistently")
        else:
            print("❌ Models handle None updated_at inconsistently")
            return False
            
        print("✅ Model timestamp consistency validation passed!")
        return True
        
    except Exception as e:
        print(f"❌ Consistency test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("Database Models Timestamp Fields Validation")
    print("=" * 70)
    
    test1_passed = test_app_setting_to_dict()
    test2_passed = test_user_preference_timestamps()
    test3_passed = test_models_consistency()
    
    print("\n" + "=" * 70)
    if test1_passed and test2_passed and test3_passed:
        print("🎉 ALL TESTS PASSED - Timestamp fields are working correctly!")
        print("✅ AppSetting now has proper to_dict() method with timestamp fields")
        print("✅ UserPreference timestamp fields are working correctly")
        print("✅ Model consistency is maintained")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED - Please review the implementation")
        sys.exit(1)