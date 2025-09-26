# RFU Hub Database Migration System - Technical Documentation

## Overview

The RFU Hub Database Migration System provides a comprehensive, production-ready solution for managing database schema evolution with complete rollback capabilities, migration tracking, and integrity validation. This system ensures safe database upgrades while maintaining data integrity and providing recovery mechanisms.

## Architecture

### Core Components

The migration system consists of four main components:

1. **DatabaseMigrationManager** - Central orchestrator for migration execution
2. **MigrationBase** - Abstract base class for migration implementations
3. **RollbackManager** - Handles rollback operations with data preservation
4. **SchemaValidator** - Validates database integrity and migration consistency

### Directory Structure

```
src/rfu/core/migrations/
├── __init__.py                    # Package initialization and exports
├── migration_manager.py           # Central migration orchestrator
├── migration_base.py             # Abstract base classes and data structures
├── rollback_manager.py           # Rollback and backup management
├── schema_validator.py           # Database integrity validation
└── migrations/                   # Individual migration implementations
    ├── __init__.py
    ├── migration_001_initial_schema.py
    └── migration_002_add_encryption_support.py
```

## DatabaseMigrationManager

### Purpose
Central orchestrator that handles the execution of database migrations with comprehensive error handling and rollback capabilities.

### Key Features
- Automatic migration discovery and dependency resolution
- Atomic migration execution with transaction management
- Migration locking to prevent concurrent execution
- Comprehensive error handling and recovery
- Integration with backup and validation systems

### Usage Example

```python
from src.rfu.core.database_manager import DatabaseManager
from src.rfu.core.migrations import DatabaseMigrationManager

# Initialize managers
db_manager = DatabaseManager()
migration_manager = DatabaseMigrationManager(db_manager)

# Check current status
status = migration_manager.get_migration_status()
print(f"Current Version: {status.current_version}")
print(f"Pending Migrations: {status.pending_migrations}")

# Execute migrations
if status.pending_migrations:
    result = migration_manager.execute_migrations()
    if result.success:
        print(f"Migrations completed in {result.execution_time_ms}ms")
    else:
        print(f"Migration failed: {result.error}")

# Rollback if needed
rollback_result = migration_manager.rollback_to_version("001")
```

### API Reference

#### `execute_migrations(target_version: Optional[str] = None) -> MigrationResult`
Executes all pending migrations up to the target version.

**Parameters:**
- `target_version`: Optional target migration version (None for latest)

**Returns:**
- `MigrationResult` with execution outcome and details

**Raises:**
- `MigrationLockError`: If migration system is locked
- `MigrationValidationError`: If validation fails

#### `rollback_to_version(target_version: str) -> RollbackResult`
Rolls back database to a specific version.

**Parameters:**
- `target_version`: Target version to rollback to

**Returns:**
- `RollbackResult` with rollback outcome and details

#### `get_migration_status() -> MigrationStatus`
Gets current migration status and pending migrations.

**Returns:**
- `MigrationStatus` with current state information

#### `validate_migration_integrity() -> ValidationResult`
Validates migration history and database integrity.

**Returns:**
- `ValidationResult` with validation outcome

## MigrationBase Abstract Class

### Purpose
Abstract base class that provides structure and validation for migration scripts.

### Required Implementation

Every migration must inherit from `MigrationBase` and implement:

```python
from src.rfu.core.migrations import MigrationBase, MigrationMetadata

class Migration001ExampleMigration(MigrationBase):
    @property
    def metadata(self) -> MigrationMetadata:
        return MigrationMetadata(
            version="001",
            description="Example migration",
            dependencies=[],
            estimated_duration_ms=5000,
            breaking_changes=False,
            rollback_supported=True
        )
    
    def up(self, connection: sqlite3.Connection) -> None:
        """Execute forward migration"""
        connection.execute("CREATE TABLE example (id INTEGER PRIMARY KEY)")
        connection.commit()
    
    def down(self, connection: sqlite3.Connection) -> None:
        """Execute rollback migration"""
        connection.execute("DROP TABLE IF EXISTS example")
        connection.commit()
    
    def validate_preconditions(self, connection: sqlite3.Connection) -> ValidationResult:
        """Validate that migration can be safely executed"""
        # Check if table already exists
        cursor = connection.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='example'
        """)
        if cursor.fetchone():
            return ValidationResult(
                success=False,
                message="Table 'example' already exists"
            )
        return ValidationResult(success=True, message="Preconditions satisfied")
    
    def validate_postconditions(self, connection: sqlite3.Connection) -> ValidationResult:
        """Validate that migration was executed successfully"""
        # Verify table was created
        cursor = connection.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='example'
        """)
        if not cursor.fetchone():
            return ValidationResult(
                success=False,
                message="Table 'example' was not created"
            )
        return ValidationResult(success=True, message="Migration completed successfully")
```

### Migration Metadata

#### MigrationMetadata Fields

- **version**: Unique version identifier (e.g., "001", "002")
- **description**: Human-readable description of the migration
- **dependencies**: List of migration versions this migration depends on
- **estimated_duration_ms**: Estimated execution time in milliseconds
- **breaking_changes**: Boolean indicating if migration introduces breaking changes
- **rollback_supported**: Boolean indicating if rollback is supported

### Validation Methods

#### `validate_preconditions(connection) -> ValidationResult`
Validates that the migration can be safely executed. Should check:
- Required tables/columns exist or don't exist as needed
- Data constraints that must be satisfied
- Dependencies are met

#### `validate_postconditions(connection) -> ValidationResult`
Validates that the migration was executed successfully. Should verify:
- Schema changes were applied correctly
- Data was migrated properly
- Constraints are satisfied

### Checksum Generation

The `get_checksum()` method automatically generates a cryptographically secure checksum of the migration content for integrity verification. This includes:
- Source code of up() and down() methods
- Migration metadata
- Deterministic salt based on class identifier

## RollbackManager

### Purpose
Manages database rollback operations with data preservation and integrity verification.

### Key Features
- Automatic backup creation before migrations
- Incremental rollback with validation at each step
- Data preservation during schema changes
- Emergency recovery procedures

### Backup Strategy

#### Backup Types
1. **Pre-migration backups**: Created before each migration execution
2. **Pre-rollback backups**: Created before rollback operations
3. **Emergency backups**: Created during recovery scenarios

#### Backup Location
Backups are stored in `data/migration_backups/` with the naming convention:
```
pre_migration_{version}_{timestamp}_{backup_id}.db
pre_rollback_{version}_{timestamp}_{backup_id}.db
emergency_{timestamp}_{backup_id}.db
```

### Usage Example

```python
from src.rfu.core.migrations import RollbackManager

# Initialize rollback manager
rollback_manager = RollbackManager(db_manager)

# Create rollback point
rollback_point = rollback_manager.create_rollback_point("002")

# Execute rollback
rollback_result = rollback_manager.execute_rollback("001")
if rollback_result.success:
    print(f"Rolled back {len(rollback_result.migrations_rolled_back)} migrations")
```

## SchemaValidator

### Purpose
Validates database schema integrity and migration consistency.

### Validation Types

#### Schema Integrity Validation
- Foreign key constraint validation
- Index integrity verification
- Data type consistency checks
- Required table existence

#### Migration Consistency Validation
- Migration history integrity
- Checksum verification
- Dependency validation
- Version sequence validation

#### Data Integrity Validation
- Timestamp format validation
- Status value validation
- Checksum verification

### Usage Example

```python
from src.rfu.core.migrations import SchemaValidator

# Initialize validator
validator = SchemaValidator(db_manager)

# Validate schema integrity
schema_result = validator.validate_schema_integrity()
if not schema_result.success:
    print(f"Schema issues: {schema_result.message}")

# Validate migration consistency
migration_result = validator.validate_migration_consistency()
if not migration_result.success:
    print(f"Migration issues: {migration_result.message}")
```

## Database Schema

### Migration Tracking Tables

#### migration_history
Tracks all applied migrations with metadata:

```sql
CREATE TABLE migration_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    applied_by TEXT DEFAULT 'system',
    execution_time_ms INTEGER NOT NULL,
    checksum TEXT NOT NULL,
    rollback_script_checksum TEXT,
    dependencies TEXT,
    breaking_changes BOOLEAN DEFAULT FALSE,
    status TEXT DEFAULT 'applied' 
        CHECK (status IN ('applied', 'rolled_back', 'failed')),
    error_message TEXT,
    backup_id TEXT
);
```

#### migration_locks
Prevents concurrent migration execution:

```sql
CREATE TABLE migration_locks (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    locked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    locked_by TEXT NOT NULL,
    migration_version TEXT,
    process_id TEXT,
    expires_at TIMESTAMP
);
```

#### migration_backups
Tracks created backups:

```sql
CREATE TABLE migration_backups (
    id TEXT PRIMARY KEY,
    migration_version TEXT NOT NULL,
    backup_type TEXT NOT NULL 
        CHECK (backup_type IN ('pre_migration', 'pre_rollback', 'emergency')),
    file_path TEXT NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    checksum TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    compression_type TEXT DEFAULT 'gzip'
);
```

#### schema_checksums
Tracks schema state after migrations:

```sql
CREATE TABLE schema_checksums (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    migration_version TEXT NOT NULL,
    table_name TEXT NOT NULL,
    schema_checksum TEXT NOT NULL,
    data_checksum TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(migration_version, table_name)
);
```

## Error Handling

### Exception Hierarchy

```python
MigrationError                    # Base migration exception
├── MigrationValidationError      # Validation failures
├── MigrationLockError           # Lock acquisition failures
└── RollbackError                # Rollback operation failures
```

### Error Recovery

#### Automatic Recovery
- Migration failure triggers automatic rollback
- Backup restoration on critical failures
- Lock timeout and cleanup

#### Emergency Recovery
- Force unlock migration system
- Restore from emergency backup
- Repair corrupted migration history
- Manual schema validation and repair

## Best Practices

### Writing Migrations

1. **Make migrations idempotent**: Use `CREATE TABLE IF NOT EXISTS`
2. **Include proper validation**: Always implement pre/post-condition validation
3. **Handle rollbacks**: Ensure `down()` method properly reverses `up()` changes
4. **Test thoroughly**: Test both forward and backward migrations
5. **Document breaking changes**: Clearly mark breaking changes in metadata

### Migration Safety

1. **Always backup**: System automatically creates backups, but verify they exist
2. **Test rollbacks**: Verify rollback procedures work correctly
3. **Monitor execution**: Watch for long-running migrations
4. **Validate dependencies**: Ensure migration dependencies are correct

### Performance Considerations

1. **Batch operations**: Use transactions for multiple operations
2. **Index management**: Drop indexes during bulk operations, recreate after
3. **Progress monitoring**: For long migrations, implement progress tracking
4. **Resource limits**: Consider memory and disk space requirements

## Troubleshooting

### Common Issues

#### Migration Lock Stuck
```bash
# Check lock status
SELECT * FROM migration_locks;

# Force unlock (use with caution)
DELETE FROM migration_locks WHERE id = 1;
```

#### Backup Restoration
```python
# Restore from specific backup
backup_id = "your-backup-id"
rollback_manager.restore_from_backup(backup_id)
```

#### Validation Failures
```python
# Run detailed validation
validation_result = validator.validate_schema_integrity()
print(validation_result.details)
```

### Debugging

#### Enable Debug Logging
```python
import logging
logging.getLogger('RFU.MigrationManager').setLevel(logging.DEBUG)
logging.getLogger('RFU.RollbackManager').setLevel(logging.DEBUG)
logging.getLogger('RFU.SchemaValidator').setLevel(logging.DEBUG)
```

#### Check Migration Status
```python
status = migration_manager.get_migration_status()
print(f"Current version: {status.current_version}")
print(f"Pending: {status.pending_migrations}")
print(f"Applied: {status.applied_migrations}")
print(f"Locked: {status.database_locked}")
```

## Integration Guide

### Adding New Migrations

1. Create new migration file in `migrations/` directory
2. Inherit from `MigrationBase`
3. Implement required methods
4. Add to `migrations/__init__.py`
5. Update migration discovery in `migration_manager.py`

### Example Integration

```python
# migrations/migration_003_add_user_settings.py
from ..migration_base import MigrationBase, MigrationMetadata, ValidationResult
import sqlite3

class Migration003AddUserSettings(MigrationBase):
    @property
    def metadata(self) -> MigrationMetadata:
        return MigrationMetadata(
            version="003",
            description="Add user settings table",
            dependencies=["002"],
            estimated_duration_ms=3000,
            breaking_changes=False,
            rollback_supported=True
        )
    
    def up(self, connection: sqlite3.Connection) -> None:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                setting_key TEXT NOT NULL,
                setting_value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, setting_key)
            )
        """)
        connection.commit()
    
    def down(self, connection: sqlite3.Connection) -> None:
        connection.execute("DROP TABLE IF EXISTS user_settings")
        connection.commit()
    
    def validate_preconditions(self, connection: sqlite3.Connection) -> ValidationResult:
        # Check dependencies are met
        cursor = connection.execute("""
            SELECT version FROM migration_history 
            WHERE version = '002' AND status = 'applied'
        """)
        if not cursor.fetchone():
            return ValidationResult(
                success=False,
                message="Migration 002 must be applied first"
            )
        return ValidationResult(success=True)
    
    def validate_postconditions(self, connection: sqlite3.Connection) -> ValidationResult:
        # Verify table was created
        cursor = connection.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='user_settings'
        """)
        if not cursor.fetchone():
            return ValidationResult(
                success=False,
                message="user_settings table was not created"
            )
        return ValidationResult(success=True)
```

### Update Migration Discovery

```python
# migrations/__init__.py
from .migration_001_initial_schema import Migration001InitialSchema
from .migration_002_add_encryption_support import Migration002AddEncryptionSupport
from .migration_003_add_user_settings import Migration003AddUserSettings

__all__ = [
    'Migration001InitialSchema',
    'Migration002AddEncryptionSupport',
    'Migration003AddUserSettings',
]
```

```python
# migration_manager.py - Update _discover_migrations method
def _discover_migrations(self) -> Dict[str, type]:
    migrations = {}
    
    try:
        from .migrations import (
            Migration001InitialSchema,
            Migration002AddEncryptionSupport,
            Migration003AddUserSettings,  # Add new migration
        )
        
        migration_classes = [
            Migration001InitialSchema,
            Migration002AddEncryptionSupport,
            Migration003AddUserSettings,  # Add new migration
        ]
        
        # ... rest of method
```

## Security Considerations

### Backup Security
- Backups contain sensitive data and should be protected
- Consider encryption for backup files
- Implement proper access controls

### Migration Safety
- Validate all input parameters
- Use parameterized queries to prevent SQL injection
- Implement proper transaction management

### Access Control
- Ensure only authorized processes can execute migrations
- Log all migration activities
- Implement audit trails

## Performance Metrics

### Monitoring

The system tracks various performance metrics:

- Migration execution time
- Backup creation time
- Validation duration
- Rollback execution time

### Optimization

- Use indexes for migration tracking queries
- Implement connection pooling
- Consider parallel validation for large schemas
- Optimize backup compression

## Conclusion

The RFU Hub Database Migration System provides a robust, production-ready solution for database schema management. With comprehensive error handling, rollback capabilities, and integrity validation, it ensures safe database evolution while maintaining data integrity and system reliability.

For additional support or questions, refer to the troubleshooting section or enable debug logging to get detailed execution information.