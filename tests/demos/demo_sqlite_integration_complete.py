"""
Comprehensive SQLite Integration Demonstration

This script demonstrates the complete SQLite integration working
with configuration management, logging, and file tracking.
"""

import sys
import logging
from pathlib import Path


def demonstrate_database_integration():
    """Demonstrate all SQLite integration features."""
    print("🎯 SQLite Integration Comprehensive Demonstration")
    print("=" * 60)

    try:
        # Initialize database system
        from standalone_database_manager import get_database_manager

        db_manager = get_database_manager()

        print("📊 Database System Status:")
        info = db_manager.get_database_info()
        print(f"   Database File: {info.get('database_file')}")
        print(f"   Database Size: {info.get('database_size_mb')} MB")
        print(f"   Session ID: {info.get('session_id')}")

        # Demonstrate configuration management
        print("\n⚙️ Configuration Management:")
        from src.core.enhanced_config_manager import (
            get_enhanced_config_manager,
        )

        config_manager = get_enhanced_config_manager()

        # Store various types of settings
        config_manager.set_setting(
            "demo", "application_name", "Richard's File Utilities"
        )
        config_manager.set_setting("demo", "version", "1.0.0")
        config_manager.set_setting("demo", "debug_mode", True)
        config_manager.set_setting("demo", "max_file_size_mb", 100)
        config_manager.set_setting(
            "demo", "supported_formats", ["pdf", "txt", "docx", "jpg"]
        )

        # Retrieve and display settings
        app_name = config_manager.get_setting("demo", "application_name")
        version = config_manager.get_setting("demo", "version")
        debug = config_manager.get_setting("demo", "debug_mode")
        max_size = config_manager.get_setting("demo", "max_file_size_mb")
        formats = config_manager.get_setting("demo", "supported_formats")

        print(f"   Application: {app_name} v{version}")
        print(f"   Debug Mode: {debug} (type: {type(debug).__name__})")
        print(
            f"   Max File Size: {max_size} MB (type: {type(max_size).__name__})"
        )
        print(
            f"   Supported Formats: {formats} (type: {type(formats).__name__})"
        )

        # Demonstrate logging integration
        print("\n📋 Database Logging:")
        from src.core.log_manager import LogManager
        from src.core.database_logging import get_database_log_service

        log_manager = LogManager()
        logger = log_manager.get_logger("Demo.Integration")

        # Create test log entries
        logger.info("Integration demonstration started")
        logger.warning(
            "This is a test warning with metadata",
            extra={"demo_data": "test_value"},
        )
        logger.error("This is a test error message")
        logger.info("Database integration working perfectly")

        # Query logs from database
        log_service = get_database_log_service()
        if log_service.enabled:
            recent_logs = log_service.get_logs(limit=10)
            print(f"   Retrieved {len(recent_logs)} recent log entries")

            # Show latest log entry
            if recent_logs:
                latest = recent_logs[0]
                print(f"   Latest: [{latest.level}] {latest.message}")

            # Get statistics
            stats = log_service.get_log_statistics()
            print(f"   Total logs: {stats.get('total_logs', 0)}")
            print(f"   By level: {stats.get('by_level', {})}")

        # Demonstrate file history tracking
        print("\n📁 File History Tracking:")

        # Simulate file access tracking
        current_file = Path(__file__)

        query = """
            INSERT OR REPLACE INTO file_history 
            (file_path, file_name, file_size, file_type, directory_path, 
             tool_name, operation_type, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        import json

        metadata = {
            "demo": True,
            "integration_test": True,
            "timestamp": "2025-08-03T22:00:00",
        }

        params = (
            str(current_file.absolute()),
            current_file.name,
            current_file.stat().st_size,
            current_file.suffix,
            str(current_file.parent.absolute()),
            "DemoTool",
            "integration_test",
            json.dumps(metadata),
        )

        affected = db_manager.execute_update(query, params)
        print(f"   File history entry: {affected} row(s) affected")

        # Query file history
        history_query = "SELECT * FROM file_history WHERE tool_name = 'DemoTool' ORDER BY last_accessed DESC LIMIT 5"
        history_results = db_manager.execute_query(history_query)

        print(f"   File history entries: {len(history_results)} found")
        for entry in history_results:
            print(
                f"     📄 {entry['file_name']} (accessed {entry['access_count']} times)"
            )

        # Demonstrate tool usage tracking
        print("\n🔧 Tool Usage Analytics:")

        # Simulate tool usage tracking
        tools_used = [
            ("FileManager", "launch"),
            ("PDFTools", "convert"),
            ("Security", "encrypt"),
            ("NetworkTools", "scan"),
            ("DemoTool", "integration_test"),
        ]

        usage_query = """
            INSERT OR IGNORE INTO tool_usage 
            (tool_name, operation_type, usage_count, success_count, first_used, last_used)
            VALUES (?, ?, 1, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """

        for tool, operation in tools_used:
            db_manager.execute_update(usage_query, (tool, operation))

        # Query usage statistics
        stats_query = """
            SELECT tool_name, operation_type, usage_count, success_count 
            FROM tool_usage ORDER BY usage_count DESC, tool_name
        """

        usage_stats = db_manager.execute_query(stats_query)
        print(f"   Tool usage entries: {len(usage_stats)} found")
        for stat in usage_stats:
            print(
                f"     🛠️ {stat['tool_name']}.{stat['operation_type']}: {stat['usage_count']} uses"
            )

        # Final database statistics
        print("\n📈 Final Database Statistics:")
        final_info = db_manager.get_database_info()
        table_counts = final_info.get("table_counts", {})
        for table, count in table_counts.items():
            print(f"   📊 {table}: {count} records")

        print(f"\n🎉 SQLite Integration Demonstration Complete!")
        print(
            f"   ✅ Database: Functional with {final_info.get('database_size_mb')} MB"
        )
        print(f"   ✅ Configuration: Type-safe storage and retrieval")
        print(f"   ✅ Logging: Structured database logging active")
        print(f"   ✅ File Tracking: Access history and analytics")
        print(f"   ✅ Tool Analytics: Usage statistics collection")

        return True

    except Exception as e:
        print(f"❌ Demonstration failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run the comprehensive demonstration."""

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    success = demonstrate_database_integration()

    if success:
        print(
            "\n✅ All SQLite integration features demonstrated successfully!"
        )
        return True
    else:
        print("\n❌ Demonstration encountered errors.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
