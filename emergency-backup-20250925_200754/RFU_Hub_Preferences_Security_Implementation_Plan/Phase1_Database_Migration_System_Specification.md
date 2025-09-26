# Phase 1: Database Migration System with Rollback Capabilities

## Technical Specification

### Overview

This specification details the implementation of a robust, versioned database migration system for the RFU Hub project that provides complete rollback capabilities, migration tracking, backward compatibility checks, automated rollback procedures, migration validation, and comprehensive error handling.

## Architecture Components

### 1. Core Migration Framework

#### 1.1 DatabaseMigrationManager

**File:** `src/rfu/core/migrations/migration_manager.py`

```python
class DatabaseMigrationManager:
    """
    Central migration orchestrator that handles the execution of database migrations
    with comprehensive error handling and rollback capabilities.
    """
    
    def __init__(self, database_manager: DatabaseManager):
        self.db_manager = database_manager
        self.logger = logging.getLogger('RFU.MigrationManager')
        self.rollback_manager = RollbackManager(database_manager)
        self.validator = SchemaValidator(database_manager)
        self.lock_manager = MigrationLockManager(database_manager)
        
    def execute_migrations(self, target_version: Optional[str] = None) -> MigrationResult:
        """Execute pending migrations up to target version"""
        
    def rollback_to_version(self, target_version: str) -> RollbackResult:
        """Rollback database to specific version"""
        
    def get_migration_status(self) -> MigrationStatus:
        """Get current migration status and pending migrations"""
        
    def validate_migration_integrity(self) -> ValidationResult:
        """Validate migration history and database integrity"""
```

**Key Features:**
- Atomic migration execution with transaction management
- Automatic backup creation before migrations
- Migration dependency resolution
- Concurrent migration prevention with locking
- Comprehensive error handling and recovery

#### 1.2 MigrationBase Abstract Class

**File:** `src/rfu/core/migrations/migration_base.py`

```python
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class MigrationMetadata:
    version: str
    description: str
    dependencies: List[str]
    estimated_duration_ms: int
    breaking_changes: bool
    rollback_supported: bool
    
class MigrationBase(ABC):
    """
    Abstract base class for all database migrations.
    Provides structure and validation for migration scripts.
    """
    
    @property
    @abstractmethod
    def metadata(self) -> MigrationMetadata:
        """Migration metadata including version, dependencies, etc."""
        pass
    
    @abstractmethod
    def up(self, connection: sqlite3.Connection) -> None:
        """Execute forward migration"""
        pass
    
    @abstractmethod
    def down(self, connection: sqlite3.Connection) -> None:
        """Execute rollback migration"""
        pass
    
    @abstractmethod
    def validate_preconditions(self, connection: sqlite3.Connection) -> ValidationResult:
        """Validate that migration can be safely executed"""
        pass
    
    @abstractmethod
    def validate_postconditions(self, connection: sqlite3.Connection) -> ValidationResult:
        """Validate that migration was executed successfully"""
        pass
    
    def get_checksum(self) -> str:
        """Generate checksum for migration integrity verification"""
        pass
```

### 2. Rollback Management System

#### 2.1 RollbackManager

**File:** `src/rfu/core/migrations/rollback_manager.py`

```python
class RollbackManager:
    """
    Manages database rollback operations with data preservation
    and integrity verification.
    """
    
    def __init__(self, database_manager: DatabaseManager):
        self.db_manager = database_manager
        self.backup_manager = MigrationBackupManager(database_manager)
        self.logger = logging.getLogger('RFU.RollbackManager')
    
    def create_rollback_point(self, version: str) -> RollbackPoint:
        """Create a rollback point before migration execution"""
        
    def execute_rollback(self, target_version: str) -> RollbackResult:
        """Execute rollback to target version"""
        
    def validate_rollback_safety(self, target_version: str) -> ValidationResult:
        """Validate that rollback can be safely performed"""
        
    def get_rollback_plan(self, target_version: str) -> RollbackPlan:
        """Generate rollback execution plan"""
```

**Rollback Features:**
- Automatic data backup before rollback
- Incremental rollback with validation at each step
- Data preservation during schema changes
- Rollback plan generation and validation
- Emergency rollback procedures

#### 2.2 Migration Backup System

```python
class MigrationBackupManager:
    """
    Handles creation and management of migration backups
    with compression and integrity verification.
    """
    
    def create_pre_migration_backup(self, migration_version: str) -> BackupResult:
        """Create backup before migration execution"""
        
    def create_rollback_backup(self, rollback_version: str) -> BackupResult:
        """Create backup before rollback execution"""
        
    def restore_from_backup(self, backup_id: str) -> RestoreResult:
        """Restore database from backup"""
        
    def cleanup_old_backups(self, retention_days: int = 30) -> CleanupResult:
        """Clean up old migration backups"""
```

### 3. Schema Validation System

#### 3.1 SchemaValidator

**File:** `src/rfu/core/migrations/schema_validator.py`

```python
class SchemaValidator:
    """
    Validates database schema integrity and migration consistency.
    """
    
    def validate_schema_integrity(self) -> ValidationResult:
        """Validate current database schema integrity"""
        
    def validate_migration_consistency(self) -> ValidationResult:
        """Validate migration history consistency"""
        
    def validate_data_integrity(self) -> ValidationResult:
        """Validate data integrity after migrations"""
        
    def generate_schema_checksum(self) -> str:
        """Generate checksum for current schema"""
        
    def compare_schemas(self, expected_schema: Dict, actual_schema: Dict) -> ComparisonResult:
        """Compare expected vs actual schema"""
```

**Validation Features:**
- Foreign key constraint validation
- Index integrity verification
- Data type consistency checks
- Migration history validation
- Schema checksum verification

### 4. Database Schema Updates

#### 4.1 Migration Tracking Tables

```sql
-- Migration history tracking
CREATE TABLE IF NOT EXISTS migration_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    applied_by TEXT DEFAULT 'system',
    execution_time_ms INTEGER NOT NULL,
    checksum TEXT NOT NULL,
    rollback_script_checksum TEXT,
    dependencies TEXT, -- JSON array of dependency versions
    breaking_changes BOOLEAN DEFAULT FALSE,
    status TEXT DEFAULT 'applied' CHECK (status IN ('applied', 'rolled_back', 'failed')),
    error_message TEXT,
    backup_id TEXT
);

-- Migration locks for concurrency control
CREATE TABLE IF NOT EXISTS migration_locks (
    id INTEGER PRIMARY KEY CHECK (id = 1), -- Ensure single row
    locked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    locked_by TEXT NOT NULL,
    migration_version TEXT,
    process_id TEXT,
    expires_at TIMESTAMP
);

-- Migration backups tracking
CREATE TABLE IF NOT EXISTS migration_backups (
    id TEXT PRIMARY KEY, -- UUID
    migration_version TEXT NOT NULL,
    backup_type TEXT NOT NULL CHECK (backup_type IN ('pre_migration', 'pre_rollback', 'emergency')),
    file_path TEXT NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    checksum TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    compression_type TEXT DEFAULT 'gzip'
);

-- Schema validation checksums
CREATE TABLE IF NOT EXISTS schema_checksums (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    migration_version TEXT NOT NULL,
    table_name TEXT NOT NULL,
    schema_checksum TEXT NOT NULL,
    data_checksum TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(migration_version, table_name)
);
```

#### 4.2 Migration Indexes

```sql
-- Performance indexes for migration operations
CREATE INDEX IF NOT EXISTS idx_migration_history_version ON migration_history(version);
CREATE INDEX IF NOT EXISTS idx_migration_history_applied_at ON migration_history(applied_at DESC);
CREATE INDEX IF NOT EXISTS idx_migration_history_status ON migration_history(status);
CREATE INDEX IF NOT EXISTS idx_migration_backups_version ON migration_backups(migration_version);
CREATE INDEX IF NOT EXISTS idx_migration_backups_created_at ON migration_backups(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_schema_checksums_version ON schema_checksums(migration_version);
```

### 5. Migration Implementation Examples

#### 5.1 Initial Schema Migration

**File:** `src/rfu/core/migrations/migrations/001_initial_schema.py`

```python
class Migration001InitialSchema(MigrationBase):
    """Initial database schema setup with security enhancements"""
    
    @property
    def metadata(self) -> MigrationMetadata:
        return MigrationMetadata(
            version="001",
            description="Initial schema setup with security tables",
            dependencies=[],
            estimated_duration_ms=5000,
            breaking_changes=False,
            rollback_supported=True
        )
    
    def up(self, connection: sqlite3.Connection) -> None:
        """Create initial schema with security enhancements"""
        
        # Create enhanced user preferences table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences_secure (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL DEFAULT 'default',
                preference_category TEXT NOT NULL,
                preference_key TEXT NOT NULL,
                encrypted_value BLOB,
                value_type TEXT NOT NULL DEFAULT 'string',
                encryption_version INTEGER DEFAULT 1,
                integrity_hash TEXT NOT NULL,
                is_pii_sensitive BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, preference_category, preference_key)
            )
        """)
        
        # Create audit log table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS preference_audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                preference_category TEXT NOT NULL,
                preference_key TEXT NOT NULL,
                operation TEXT NOT NULL CHECK (operation IN ('create', 'read', 'update', 'delete')),
                old_value_hash TEXT,
                new_value_hash TEXT,
                ip_address TEXT,
                user_agent TEXT,
                session_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT TRUE,
                error_message TEXT
            )
        """)
        
        connection.commit()
    
    def down(self, connection: sqlite3.Connection) -> None:
        """Rollback initial schema"""
        connection.execute("DROP TABLE IF EXISTS preference_audit_log")
        connection.execute("DROP TABLE IF EXISTS user_preferences_secure")
        connection.commit()
    
    def validate_preconditions(self, connection: sqlite3.Connection) -> ValidationResult:
        """Validate that migration can be safely executed"""
        # Check if tables already exist
        cursor = connection.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('user_preferences_secure', 'preference_audit_log')
        """)
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        if existing_tables:
            return ValidationResult(
                success=False,
                message=f"Tables already exist: {existing_tables}"
            )
        
        return ValidationResult(success=True, message="Preconditions satisfied")
    
    def validate_postconditions(self, connection: sqlite3.Connection) -> ValidationResult:
        """Validate that migration was executed successfully"""
        # Verify tables were created
        cursor = connection.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN ('user_preferences_secure', 'preference_audit_log')
        """)
        created_tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['user_preferences_secure', 'preference_audit_log']
        if set(created_tables) != set(expected_tables):
            return ValidationResult(
                success=False,
                message=f"Expected tables {expected_tables}, found {created_tables}"
            )
        
        return ValidationResult(success=True, message="Migration completed successfully")
```

#### 5.2 Encryption Support Migration

**File:** `src/rfu/core/migrations/migrations/002_add_encryption_support.py`

```python
class Migration002AddEncryptionSupport(MigrationBase):
    """Add encryption support for theme data"""
    
    @property
    def metadata(self) -> MigrationMetadata:
        return MigrationMetadata(
            version="002",
            description="Add encryption support for theme data storage",
            dependencies=["001"],
            estimated_duration_ms=10000,
            breaking_changes=False,
            rollback_supported=True
        )
    
    def up(self, connection: sqlite3.Connection) -> None:
        """Add encryption support tables"""
        
        # Create secure themes table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS secure_themes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL DEFAULT 'default',
                theme_name TEXT NOT NULL,
                encrypted_data BLOB NOT NULL,
                integrity_hash TEXT NOT NULL,
                encryption_version INTEGER DEFAULT 1,
                theme_version TEXT DEFAULT '1.0',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                last_accessed TIMESTAMP,
                UNIQUE(user_id, theme_name)
            )
        """)
        
        # Create theme access audit log
        connection.execute("""
            CREATE TABLE IF NOT EXISTS theme_access_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                theme_name TEXT NOT NULL,
                operation TEXT NOT NULL CHECK (operation IN ('read', 'write', 'delete', 'export', 'import')),
                ip_address TEXT,
                user_agent TEXT,
                session_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT TRUE,
                error_message TEXT,
                data_size_bytes INTEGER
            )
        """)
        
        # Create encryption keys table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS encryption_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_id TEXT NOT NULL UNIQUE,
                key_type TEXT NOT NULL CHECK (key_type IN ('theme', 'preference', 'directory')),
                encrypted_key BLOB NOT NULL,
                salt BLOB NOT NULL,
                key_version INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        """)
        
        connection.commit()
    
    def down(self, connection: sqlite3.Connection) -> None:
        """Rollback encryption support"""
        connection.execute("DROP TABLE IF EXISTS encryption_keys")
        connection.execute("DROP TABLE IF EXISTS theme_access_log")
        connection.execute("DROP TABLE IF EXISTS secure_themes")
        connection.commit()
    
    def validate_preconditions(self, connection: sqlite3.Connection) -> ValidationResult:
        """Validate dependencies and prerequisites"""
        # Check that migration 001 was applied
        cursor = connection.execute("""
            SELECT version FROM migration_history 
            WHERE version = '001' AND status = 'applied'
        """)
        if not cursor.fetchone():
            return ValidationResult(
                success=False,
                message="Migration 001 must be applied before migration 002"
            )
        
        return ValidationResult(success=True, message="Dependencies satisfied")
    
    def validate_postconditions(self, connection: sqlite3.Connection) -> ValidationResult:
        """Validate encryption tables were created"""
        expected_tables = ['secure_themes', 'theme_access_log', 'encryption_keys']
        
        cursor = connection.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name IN (?, ?, ?)
        """, expected_tables)
        created_tables = [row[0] for row in cursor.fetchall()]
        
        if set(created_tables) != set(expected_tables):
            return ValidationResult(
                success=False,
                message=f"Expected tables {expected_tables}, found {created_tables}"
            )
        
        return ValidationResult(success=True, message="Encryption support added successfully")
```

### 6. Error Handling and Recovery

#### 6.1 Migration Error Handling

```python
class MigrationError(Exception):
    """Base exception for migration errors"""
    pass

class MigrationValidationError(MigrationError):
    """Raised when migration validation fails"""
    pass

class RollbackError(MigrationError):
    """Raised when rollback operation fails"""
    pass

class MigrationLockError(MigrationError):
    """Raised when migration lock cannot be acquired"""
    pass

class MigrationErrorHandler:
    """Handles migration errors with automatic recovery"""
    
    def handle_migration_failure(self, migration: MigrationBase, error: Exception) -> RecoveryResult:
        """Handle migration failure with automatic rollback"""
        
    def handle_rollback_failure(self, target_version: str, error: Exception) -> RecoveryResult:
        """Handle rollback failure with emergency procedures"""
        
    def create_error_report(self, error: Exception, context: Dict[str, Any]) -> ErrorReport:
        """Create detailed error report for debugging"""
```

#### 6.2 Emergency Recovery Procedures

```python
class EmergencyRecoveryManager:
    """Handles emergency database recovery scenarios"""
    
    def emergency_rollback_to_backup(self, backup_id: str) -> RecoveryResult:
        """Emergency rollback using backup file"""
        
    def repair_corrupted_migration_history(self) -> RepairResult:
        """Repair corrupted migration history table"""
        
    def force_unlock_migrations(self) -> bool:
        """Force unlock migration system in emergency"""
        
    def validate_and_repair_schema(self) -> RepairResult:
        """Validate and repair database schema"""
```

### 7. Performance Optimization

#### 7.1 Migration Performance Features

- **Batch Operations**: Execute multiple schema changes in single transaction
- **Index Management**: Drop indexes before bulk operations, recreate after
- **Connection Pooling**: Reuse database connections for migration operations
- **Progress Tracking**: Real-time progress updates for long-running migrations
- **Parallel Validation**: Concurrent validation of multiple migration aspects

#### 7.2 Monitoring and Metrics

```python
class MigrationMetrics:
    """Collects and reports migration performance metrics"""
    
    def record_migration_duration(self, version: str, duration_ms: int) -> None:
        """Record migration execution time"""
        
    def record_rollback_duration(self, version: str, duration_ms: int) -> None:
        """Record rollback execution time"""
        
    def get_performance_report(self) -> PerformanceReport:
        """Generate migration performance report"""
```

### 8. Testing Strategy

#### 8.1 Unit Tests

- Migration execution logic
- Rollback functionality
- Validation mechanisms
- Error handling
- Lock management

#### 8.2 Integration Tests

- End-to-end migration scenarios
- Rollback to various versions
- Concurrent migration prevention
- Backup and restore operations
- Schema validation

#### 8.3 Stress Tests

- Large database migrations
- Multiple rapid migrations
- Rollback under load
- Concurrent access during migrations
- Recovery from various failure scenarios

## Implementation Checklist

### Core Framework
- [ ] Implement `DatabaseMigrationManager`
- [ ] Create `MigrationBase` abstract class
- [ ] Build `RollbackManager`
- [ ] Develop `SchemaValidator`
- [ ] Create migration lock system

### Database Schema
- [ ] Create migration tracking tables
- [ ] Add performance indexes
- [ ] Implement audit triggers
- [ ] Create backup tracking

### Migration Scripts
- [ ] Implement initial schema migration
- [ ] Create encryption support migration
- [ ] Build directory security migration
- [ ] Add validation migrations

### Error Handling
- [ ] Implement error handling framework
- [ ] Create emergency recovery procedures
- [ ] Build error reporting system
- [ ] Add monitoring and metrics

### Testing
- [ ] Write comprehensive unit tests
- [ ] Create integration test suite
- [ ] Implement stress testing
- [ ] Add performance benchmarks

This specification provides a comprehensive foundation for implementing a robust database migration system with complete rollback capabilities, ensuring safe schema evolution while maintaining data integrity and system reliability.