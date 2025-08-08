"""
Simple test for SQLite integration Phase 1 - Standalone version

This script tests the core database functionality without complex imports.
"""

import sys
import logging

def test_standalone_database():
    """Test standalone database manager."""
    print("🔍 Testing Standalone Database Manager...")
    
    try:
        from standalone_database_manager import get_database_manager
        
        db_manager = get_database_manager()
        
        # Test database info
        info = db_manager.get_database_info()
        print(f"✅ Database initialized: {info.get('database_file')}")
        print(f"✅ Database size: {info.get('database_size_mb', 0)} MB")
        print(f"✅ Session ID: {info.get('session_id')}")
        
        # Test table counts
        table_counts = info.get('table_counts', {})
        for table, count in table_counts.items():
            print(f"   📊 {table}: {count} records")
        
        # Test setting storage and retrieval
        setting_test = db_manager.get_setting('database', 'auto_vacuum', False)
        print(f"✅ Setting retrieval: auto_vacuum = {setting_test}")
        
        # Test file history insertion
        query = """
            INSERT OR REPLACE INTO file_history 
            (file_path, file_name, file_size, file_type, directory_path, 
             tool_name, operation_type, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            __file__,
            'test_simple.py',
            1024,
            '.py',
            '.',
            'TestTool',
            'validation',
            '{"test": true}'
        )
        
        affected = db_manager.execute_update(query, params)
        print(f"✅ File history test: {affected} row(s) affected")
        
        # Test app_logs insertion
        log_query = """
            INSERT INTO app_logs 
            (level, logger_name, message, tool_name, session_id)
            VALUES (?, ?, ?, ?, ?)
        """
        
        log_params = (
            'INFO',
            'Test.Logger',
            'Test log message for database validation',
            'TestTool',
            info.get('session_id')
        )
        
        log_affected = db_manager.execute_update(log_query, log_params)
        print(f"✅ Log entry test: {log_affected} row(s) affected")
        
        # Get updated counts
        updated_info = db_manager.get_database_info()
        updated_counts = updated_info.get('table_counts', {})
        print(f"✅ Updated table counts:")
        for table, count in updated_counts.items():
            print(f"   📊 {table}: {count} records")
        
        return True
        
    except Exception as e:
        print(f"❌ Standalone Database Manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run simple database test."""
    print("🧪 SQLite Integration - Simple Database Test")
    print("=" * 50)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    success = test_standalone_database()
    
    print("\n📊 Simple Test Results")
    print("=" * 50)
    
    if success:
        print("🎉 Simple database test passed! Core SQLite integration working!")
        return True
    else:
        print("❌ Simple database test failed.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
