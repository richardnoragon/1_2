"""
Test script for SQLite integration - Phase 1 validation

This script tests the database manager, enhanced configuration manager,
and database logging functionality.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_database_manager():
    """Test database manager functionality."""
    print("🔍 Testing Database Manager...")

    try:
        from src.database.database_manager import get_database_manager

        db_manager = get_database_manager()

        # Test database info
        info = db_manager.get_database_info()
        print(f"✅ Database initialized: {info.get('database_file')}")
        print(f"✅ Database size: {info.get('database_size_mb', 0)} MB")
        print(f"✅ Session ID: {info.get('session_id')}")

        # Test table counts
        table_counts = info.get("table_counts", {})
        for table, count in table_counts.items():
            print(f"   📊 {table}: {count} records")

        # Test setting storage with validation
        setting_test = db_manager.get_setting("database", "auto_vacuum", False)
        if not isinstance(setting_test, bool):
            print(
                f"❌ Validation failed: auto_vacuum should be bool, got {type(setting_test)}"
            )
            return False
        print(f"✅ Setting retrieval test: auto_vacuum = {setting_test}")

        return True

    except Exception as e:
        print(f"❌ Database Manager test failed: {e}")
        return False


def test_enhanced_config_manager():
    """Test enhanced configuration manager."""
    print("\n🔍 Testing Enhanced Configuration Manager...")

    try:
        from src.core.enhanced_config_manager import get_enhanced_config_manager

        config_manager = get_enhanced_config_manager()

        # Test setting operations with validation
        test_data = {
            "string_value": "hello world",
            "integer_value": 42,
            "boolean_value": True,
            "json_value": {"key": "value", "list": [1, 2, 3]},
        }

        # Set values
        for key, value in test_data.items():
            config_manager.set_setting("test", key, value)

        # Test retrieval with validation
        string_val = config_manager.get_setting("test", "string_value")
        integer_val = config_manager.get_setting("test", "integer_value")
        boolean_val = config_manager.get_setting("test", "boolean_value")
        json_val = config_manager.get_setting("test", "json_value")

        # Validate types and values
        if not isinstance(string_val, str) or string_val != "hello world":
            print(f"❌ String validation failed: {string_val}")
            return False

        if not isinstance(integer_val, int) or integer_val != 42:
            print(f"❌ Integer validation failed: {integer_val}")
            return False

        if not isinstance(boolean_val, bool) or boolean_val is not True:
            print(f"❌ Boolean validation failed: {boolean_val}")
            return False

        if not isinstance(json_val, dict) or json_val.get("key") != "value":
            print(f"❌ JSON validation failed: {json_val}")
            return False

        print(f"✅ String setting: {string_val}")
        print(f"✅ Integer setting: {integer_val}")
        print(f"✅ Boolean setting: {boolean_val}")
        print(f"✅ JSON setting: {json_val}")

        # Test section retrieval
        test_section = config_manager.get_section("test")
        if len(test_section) < 4:  # Should have at least our 4 test settings
            print(f"❌ Section validation failed: only {len(test_section)} settings")
            return False
        print(f"✅ Section retrieval: {len(test_section)} settings in 'test' section")

        # Get config info
        config_info = config_manager.get_config_info()
        print(f"✅ Configuration backend: {config_info.get('backend')}")
        print(f"✅ Total settings: {config_info.get('total_settings', 0)}")

        return True

    except Exception as e:
        print(f"❌ Enhanced Configuration Manager test failed: {e}")
        return False


def test_database_logging():
    """Test database logging functionality."""
    print("\n🔍 Testing Database Logging...")

    try:
        from src.core.database_logging import get_database_log_service
        from src.core.log_manager import LogManager

        # Initialize log manager (this should set up database logging)
        log_manager = LogManager()
        logger = log_manager.get_logger("Test.DatabaseLogging")

        # Create test log entries
        logger.info("Test info message for database logging")
        logger.warning(
            "Test warning message with metadata", extra={"test_metadata": "value"}
        )
        logger.error("Test error message")

        # Test database log service
        log_service = get_database_log_service()

        if log_service.enabled:
            # Get recent logs
            recent_logs = log_service.get_logs(limit=5)
            print(f"✅ Retrieved {len(recent_logs)} recent log entries")

            # Validate log entry structure
            for log_entry in recent_logs:
                if not isinstance(log_entry, dict):
                    print(f"⚠️ Invalid log entry type: {type(log_entry)}")
                    return False

                # Check required fields
                required_fields = ["message", "level", "timestamp"]
                for field in required_fields:
                    if field not in log_entry:
                        print(f"⚠️ Missing required field '{field}' in log entry")
                        return False
                    if log_entry[field] is None:
                        print(f"⚠️ Null value for required field '{field}'")
                        return False

            # Get log statistics
            stats = log_service.get_log_statistics()
            print(f"✅ Total logs in database: {stats.get('total_logs', 0)}")

            # Validate statistics structure
            by_level = stats.get("by_level", {})
            if isinstance(by_level, dict):
                print(f"✅ Logs by level: {by_level}")

                # Validate log level data types
                for level, count in by_level.items():
                    if not isinstance(level, str):
                        print(f"⚠️ Invalid log level type: {type(level)}")
                        return False
                    if not isinstance(count, int) or count < 0:
                        print(f"⚠️ Invalid log count for {level}: {count}")
                        return False
            else:
                print("⚠️ Invalid log statistics format")
                return False

            return True
        else:
            print("⚠️ Database logging service not enabled")
            return False

    except Exception as e:
        print(f"❌ Database Logging test failed: {e}")
        return False


def test_file_history_tracking():
    """Test file history tracking capability."""
    print("\n🔍 Testing File History Tracking...")

    try:
        from src.core.database_models import FileHistory
        from src.database.database_manager import get_database_manager

        db_manager = get_database_manager()

        # Create test file history entry
        test_file = FileHistory(
            file_path=str(Path(__file__).absolute()),
            file_name=Path(__file__).name,
            file_size=Path(__file__).stat().st_size,
            file_type=".py",
            directory_path=str(Path(__file__).parent.absolute()),
            tool_name="TestTool",
            operation_type="test",
            metadata={"test": True, "source": "integration_test"},
        )

        # Insert into database
        query = """
            INSERT OR REPLACE INTO file_history 
            (file_path, file_name, file_size, file_type, directory_path, 
             tool_name, operation_type, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            test_file.file_path,
            test_file.file_name,
            test_file.file_size,
            test_file.file_type,
            test_file.directory_path,
            test_file.tool_name,
            test_file.operation_type,
            '{"test": true, "source": "integration_test"}',
        )

        affected = db_manager.execute_update(query, params)
        print(f"✅ File history entry created/updated: {affected} row(s) affected")

        # Retrieve the entry
        retrieve_query = "SELECT * FROM file_history WHERE file_path = ?"
        results = db_manager.execute_query(retrieve_query, (test_file.file_path,))

        if results:
            entry = results[0]
            print(f"✅ Retrieved file history: {entry['file_name']}")
            print(f"   📁 Directory: {entry['directory_path']}")
            print(f"   🔧 Tool: {entry['tool_name']}")
            print(f"   📊 Access count: {entry['access_count']}")

            # Validate file history entry structure
            required_fields = ["file_path", "file_name", "tool_name", "access_count"]
            for field in required_fields:
                if field not in entry:
                    print(f"⚠️ Missing required field '{field}' in file history entry")
                    return False
                if entry[field] is None:
                    print(f"⚠️ Null value for required field '{field}'")
                    return False

            # Validate data types
            if not isinstance(entry["access_count"], int) or entry["access_count"] < 0:
                print(f"⚠️ Invalid access_count: {entry['access_count']}")
                return False

            if not isinstance(entry["file_name"], str) or not entry["file_name"]:
                print(f"⚠️ Invalid file_name: {entry['file_name']}")
                return False
        else:
            print("⚠️ No file history entry found")
            return False

    except Exception as e:
        print(f"❌ File History Tracking test failed: {e}")
        return False


def main():
    """Run all integration tests."""
    print("🧪 SQLite Integration Tests - Phase 1")
    print("=" * 50)

    results = []

    # Test database manager
    results.append(test_database_manager())

    # Test enhanced configuration manager
    results.append(test_enhanced_config_manager())

    # Test database logging
    results.append(test_database_logging())

    # Test file history tracking
    results.append(test_file_history_tracking())

    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 50)

    passed = sum(results)
    total = len(results)

    print(f"✅ Tests passed: {passed}/{total}")

    if passed == total:
        print("🎉 All tests passed! SQLite integration Phase 1 successful!")
        return True
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
