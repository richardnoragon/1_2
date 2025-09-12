"""
Migration System Integration Test

Tests the database migration system integration with the main database manager.
"""

import sys
import os
import sqlite3
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.rfu.core.database_manager import DatabaseManager
from src.rfu.core.migrations import DatabaseMigrationManager


def test_migration_system():
    """Test the migration system integration."""
    print("=== RFU Hub Migration System Integration Test ===\n")
    
    try:
        # Initialize database manager
        print("1. Initializing Database Manager...")
        db_manager = DatabaseManager()
        print("   ✅ Database Manager initialized successfully")
        
        # Initialize migration manager
        print("\n2. Initializing Migration Manager...")
        migration_manager = DatabaseMigrationManager(db_manager)
        print("   ✅ Migration Manager initialized successfully")
        
        # Check current migration status
        print("\n3. Checking Current Migration Status...")
        status = migration_manager.get_migration_status()
        print(f"   Current Version: {status.current_version}")
        print(f"   Pending Migrations: {len(status.pending_migrations)}")
        for migration in status.pending_migrations:
            print(f"     - {migration}")
        
        # Execute pending migrations
        if status.pending_migrations:
            print("\n4. Executing Pending Migrations...")
            result = migration_manager.execute_migrations()
            print(f"   Migration Result: {result.success}")
            if result.success:
                print(f"   Final Version: {result.version}")
                print(f"   Execution Time: {result.execution_time_ms}ms")
                print("   ✅ All migrations applied successfully")
            else:
                print(f"   Error: {result.error}")
                print("   ❌ Migration failed")
        else:
            print("\n4. No pending migrations found")
            print("   ✅ Database is up to date")
        
        # Validate database integrity
        print("\n5. Validating Database Integrity...")
        validation = migration_manager.validate_migration_integrity()
        if validation.success:
            print("   ✅ Database integrity validated successfully")
        else:
            print(f"   ❌ Integrity validation failed: {validation.message}")
        
        print("\n=== Migration System Test Completed Successfully ===")
        return True
        
    except Exception as e:
        print(f"\n❌ Migration system test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_migration_system()
    if success:
        print("\n🎉 Migration system is ready for use!")
    else:
        print("\n💥 Migration system needs attention!")
        sys.exit(1)