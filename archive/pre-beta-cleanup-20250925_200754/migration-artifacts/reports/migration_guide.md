# RFU Hub Security Framework - Migration Guide

## Overview

This guide provides comprehensive instructions for migrating to the RFU Hub Security Framework, covering database migrations, security setting transitions, and compatibility considerations for all implementation phases.

## Table of Contents

1. [Migration Overview](#migration-overview)
2. [Pre-Migration Requirements](#pre-migration-requirements)
3. [Phase-by-Phase Migration](#phase-by-phase-migration)
4. [Database Migration Procedures](#database-migration-procedures)
5. [Security Setting Transitions](#security-setting-transitions)
6. [Data Migration and Backup](#data-migration-and-backup)
7. [Compatibility Considerations](#compatibility-considerations)
8. [Post-Migration Verification](#post-migration-verification)
9. [Rollback Procedures](#rollback-procedures)
10. [Troubleshooting](#troubleshooting)

---

## Migration Overview

The RFU Hub Security Framework migration involves transitioning from basic directory preference storage to a comprehensive security-enhanced system with encryption, PII detection, audit logging, and permission management.

### Migration Phases

| Phase | Description | Key Features | Migration Time |
|-------|-------------|--------------|----------------|
| **Phase 1** | Basic Security Foundation | Database encryption, core security | 15-30 minutes |
| **Phase 2** | PII Detection & Permissions | PII scanning, RBAC system | 20-45 minutes |
| **Phase 3** | Comprehensive Auditing | Full audit logging, security events | 10-30 minutes |
| **Phase 4** | Integration & Testing | Testing frameworks, documentation | N/A (Testing) |

### Migration Strategy

- **Progressive Enhancement:** Each phase builds upon the previous
- **Backward Compatibility:** Existing data preserved and enhanced
- **Zero Downtime:** Migrations designed for minimal service interruption
- **Rollback Support:** Full rollback capability for each phase

---

## Pre-Migration Requirements

### System Requirements

**Minimum Requirements:**
- Python 3.8 or higher
- SQLite 3.35 or higher
- 2GB available disk space
- 4GB RAM recommended

**Software Dependencies:**
```bash
# Core dependencies
pip install cryptography>=3.4.8
pip install sqlite3
pip install hashlib
pip install hmac

# Optional dependencies for enhanced features
pip install psutil>=5.8.0  # Performance monitoring
pip install pytest>=6.0.0  # Testing framework
```

### Backup Requirements

**Critical Data Backup:**
1. **Database Files:** Complete database backup
2. **Configuration Files:** All configuration and settings
3. **User Data:** Existing directory preferences
4. **Application State:** Current application configuration

### Environment Preparation

```bash
# Create migration workspace
mkdir rfu_migration_workspace
cd rfu_migration_workspace

# Create backup directory
mkdir backups
mkdir logs
mkdir temp

# Set environment variables
export RFU_MIGRATION_LOG_LEVEL=INFO
export RFU_BACKUP_PATH=$(pwd)/backups
export RFU_TEMP_PATH=$(pwd)/temp
```

---

## Phase-by-Phase Migration

### Phase 1: Basic Security Foundation

**Duration:** 15-30 minutes  
**Scope:** Database encryption, core security infrastructure

#### Pre-Phase 1 Checklist

- [ ] Complete system backup
- [ ] Verify Python and SQLite versions
- [ ] Install cryptography dependencies
- [ ] Test database connectivity
- [ ] Validate existing data integrity

#### Migration Steps

```bash
# Step 1: Initialize migration environment
python -m rfu.migration.phase1_migration --init

# Step 2: Backup existing database
python -m rfu.migration.backup_manager --backup-all --phase=1

# Step 3: Apply Phase 1 migrations
python -m rfu.migration.migration_manager --apply-phase=1

# Step 4: Verify migration success
python -m rfu.migration.verification --phase=1
```

#### Phase 1 Database Changes

```sql
-- New tables added
CREATE TABLE directories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    tool_id TEXT NOT NULL,
    category TEXT NOT NULL,
    path_hash TEXT UNIQUE NOT NULL,
    encrypted_path BLOB NOT NULL,
    salt BLOB NOT NULL,
    nonce BLOB NOT NULL,
    integrity_hash TEXT NOT NULL,
    -- ... additional fields
);

CREATE TABLE encryption_keys (
    -- Key metadata table
);
```

#### Post-Phase 1 Verification

```python
# Verification script
from rfu.migration.verification import Phase1Verifier

verifier = Phase1Verifier()
results = verifier.verify_migration()

if results.success:
    print("✅ Phase 1 migration completed successfully")
    print(f"Encrypted directories: {results.encrypted_count}")
    print(f"Migration time: {results.duration}")
else:
    print("❌ Phase 1 migration failed")
    print(f"Errors: {results.errors}")
```

### Phase 2: PII Detection & Permissions

**Duration:** 20-45 minutes  
**Scope:** PII scanning, role-based access control

#### Pre-Phase 2 Checklist

- [ ] Phase 1 completed successfully
- [ ] Database integrity verified
- [ ] Additional disk space available (for PII analysis)
- [ ] Performance baseline established

#### Migration Steps

```bash
# Step 1: Pre-migration PII analysis
python -m rfu.migration.pii_analyzer --analyze-existing-data

# Step 2: Apply Phase 2 migrations
python -m rfu.migration.migration_manager --apply-phase=2

# Step 3: Execute PII detection on existing data
python -m rfu.migration.pii_migration --scan-all-directories

# Step 4: Initialize permission system
python -m rfu.migration.permission_migration --initialize-permissions

# Step 5: Verify Phase 2 completion
python -m rfu.migration.verification --phase=2
```

#### Phase 2 Database Changes

```sql
-- PII detection tables
CREATE TABLE pii_detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    directory_id INTEGER NOT NULL,
    pii_type TEXT NOT NULL,
    confidence_score REAL NOT NULL,
    -- ... additional fields
);

-- Permission management
CREATE TABLE directory_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    permission_type TEXT NOT NULL,
    -- ... additional fields
);
```

#### PII Migration Process

```python
# PII migration example
from rfu.migration.pii_migration import PIIMigrationManager

pii_migrator = PIIMigrationManager()

# Scan existing directories for PII
results = pii_migrator.scan_existing_directories()
print(f"Scanned {results.total_directories} directories")
print(f"Found PII in {results.pii_directories} directories")

# Apply enhanced security to PII-sensitive directories
pii_migrator.apply_enhanced_security(results.pii_directories)
```

### Phase 3: Comprehensive Auditing

**Duration:** 10-30 minutes  
**Scope:** Audit logging, security event tracking

#### Pre-Phase 3 Checklist

- [ ] Phase 2 completed successfully
- [ ] PII classification completed
- [ ] Permission system operational
- [ ] Log storage capacity verified

#### Migration Steps

```bash
# Step 1: Initialize audit system
python -m rfu.migration.audit_migration --initialize

# Step 2: Apply Phase 3 migrations
python -m rfu.migration.migration_manager --apply-phase=3

# Step 3: Migrate historical data to audit format
python -m rfu.migration.audit_migration --migrate-historical

# Step 4: Configure security event monitoring
python -m rfu.migration.security_events --configure

# Step 5: Verify audit system
python -m rfu.migration.verification --phase=3
```

#### Phase 3 Database Changes

```sql
-- Audit logging
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id TEXT NOT NULL,
    operation_type TEXT NOT NULL,
    -- ... additional fields
);

-- Security events
CREATE TABLE security_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    event_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    -- ... additional fields
);
```

---

## Database Migration Procedures

### Automated Migration Process

```python
# Complete migration automation
from rfu.migration.migration_manager import MigrationManager

def execute_full_migration():
    """Execute complete migration process"""
    migration_manager = MigrationManager()
    
    try:
        # Phase 1: Basic Security
        phase1_result = migration_manager.apply_phase_1()
        if not phase1_result.success:
            raise MigrationError(f"Phase 1 failed: {phase1_result.error}")
        
        # Phase 2: PII & Permissions
        phase2_result = migration_manager.apply_phase_2()
        if not phase2_result.success:
            raise MigrationError(f"Phase 2 failed: {phase2_result.error}")
        
        # Phase 3: Auditing
        phase3_result = migration_manager.apply_phase_3()
        if not phase3_result.success:
            raise MigrationError(f"Phase 3 failed: {phase3_result.error}")
        
        return MigrationResult(
            success=True,
            total_time=sum([p.duration for p in [phase1_result, phase2_result, phase3_result]]),
            migrated_records=sum([p.records for p in [phase1_result, phase2_result, phase3_result]])
        )
    
    except Exception as e:
        # Automatic rollback on failure
        migration_manager.rollback_all()
        raise MigrationError(f"Migration failed: {e}")

# Execute migration
result = execute_full_migration()
print(f"Migration completed in {result.total_time} seconds")
```

### Manual Migration Steps

For environments requiring manual control:

```sql
-- Manual Phase 1 Migration
BEGIN TRANSACTION;

-- Create new security tables
CREATE TABLE directories_new (
    -- New schema with security fields
);

-- Migrate existing data
INSERT INTO directories_new (user_id, tool_id, category, path_hash, encrypted_path, ...)
SELECT 
    user_id, 
    tool_id, 
    category,
    sha256(directory_path) as path_hash,
    encrypt_path(directory_path, generate_key(user_id)) as encrypted_path,
    -- ... encryption fields
FROM directories_old;

-- Verify migration
SELECT COUNT(*) FROM directories_new;
SELECT COUNT(*) FROM directories_old;

-- Replace old table
DROP TABLE directories_old;
ALTER TABLE directories_new RENAME TO directories;

COMMIT;
```

### Migration Performance Optimization

```python
# Performance optimization for large datasets
class OptimizedMigration:
    def __init__(self, batch_size=1000):
        self.batch_size = batch_size
    
    def migrate_large_dataset(self, total_records):
        """Migrate large datasets in batches"""
        batches = (total_records // self.batch_size) + 1
        
        for batch_num in range(batches):
            offset = batch_num * self.batch_size
            
            # Process batch
            batch_records = self.get_batch_records(offset, self.batch_size)
            self.process_batch(batch_records)
            
            # Progress reporting
            progress = min(((batch_num + 1) * self.batch_size), total_records)
            print(f"Migrated {progress}/{total_records} records ({progress/total_records*100:.1f}%)")
            
            # Memory cleanup
            gc.collect()
```

---

## Security Setting Transitions

### Encryption Configuration

**From:** Plain text directory storage  
**To:** AES-256-GCM encrypted storage

```python
# Migration configuration
ENCRYPTION_CONFIG = {
    'algorithm': 'AES-256-GCM',
    'key_derivation': 'PBKDF2-HMAC-SHA256',
    'iterations': 100000,
    'salt_size': 32,
    'nonce_size': 12
}

# Apply encryption to existing data
def migrate_encryption_settings():
    """Migrate from plain text to encrypted storage"""
    
    # Load existing directories
    existing_directories = load_existing_directories()
    
    for directory in existing_directories:
        # Generate encryption parameters
        salt = generate_salt()
        nonce = generate_nonce()
        key = derive_key(directory.user_id, salt)
        
        # Encrypt directory path
        encrypted_path = encrypt_path(directory.path, key, nonce)
        integrity_hash = generate_integrity_hash(encrypted_path, key)
        
        # Update database record
        update_directory_security(
            directory.id,
            encrypted_path=encrypted_path,
            salt=salt,
            nonce=nonce,
            integrity_hash=integrity_hash
        )
```

### PII Detection Configuration

```python
# PII detection migration
PII_CONFIG = {
    'detection_rules': [
        'personal_names',
        'ssn_patterns',
        'credit_card_patterns',
        'email_patterns',
        'phone_patterns'
    ],
    'confidence_threshold': 0.7,
    'enhanced_security_threshold': 0.9
}

def migrate_pii_detection():
    """Apply PII detection to existing directories"""
    
    pii_detector = PIIDetector(PII_CONFIG)
    directories = get_all_directories()
    
    for directory in directories:
        # Decrypt path for analysis
        decrypted_path = decrypt_directory_path(directory)
        
        # Detect PII
        pii_result = pii_detector.detect_pii(decrypted_path)
        
        # Store PII detection results
        if pii_result.has_pii:
            store_pii_detection(
                directory.id,
                pii_types=pii_result.pii_types,
                confidence=pii_result.confidence_score
            )
            
            # Apply enhanced security
            apply_enhanced_security(directory.id)
```

### Permission System Migration

```python
# Permission migration from simple access to RBAC
def migrate_permission_system():
    """Migrate to role-based access control"""
    
    # Default permissions for existing users
    DEFAULT_PERMISSIONS = {
        'read': True,
        'write': True,
        'execute': True,
        'share': False,  # Restrictive by default
        'delete': True
    }
    
    # Get all existing user-directory relationships
    user_directories = get_user_directory_relationships()
    
    for user_id, directory_hash in user_directories:
        # Apply default permissions
        for permission_type, granted in DEFAULT_PERMISSIONS.items():
            set_permission(
                user_id=user_id,
                resource_id=directory_hash,
                permission_type=permission_type,
                granted=granted,
                granted_by='migration_system'
            )
```

---

## Data Migration and Backup

### Comprehensive Backup Strategy

```python
# Comprehensive backup before migration
class MigrationBackupManager:
    def __init__(self, backup_path):
        self.backup_path = backup_path
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def create_full_backup(self):
        """Create complete system backup"""
        backup_info = {
            'timestamp': self.timestamp,
            'components': []
        }
        
        # Database backup
        db_backup = self.backup_database()
        backup_info['components'].append(db_backup)
        
        # Configuration backup
        config_backup = self.backup_configurations()
        backup_info['components'].append(config_backup)
        
        # User data backup
        user_backup = self.backup_user_data()
        backup_info['components'].append(user_backup)
        
        # Create backup manifest
        self.create_backup_manifest(backup_info)
        
        return backup_info
    
    def backup_database(self):
        """Backup database with verification"""
        source_db = get_database_path()
        backup_db = os.path.join(
            self.backup_path, 
            f'database_backup_{self.timestamp}.db'
        )
        
        # Create backup
        shutil.copy2(source_db, backup_db)
        
        # Verify backup integrity
        if self.verify_database_backup(backup_db):
            return {
                'type': 'database',
                'source': source_db,
                'backup': backup_db,
                'size': os.path.getsize(backup_db),
                'verified': True
            }
        else:
            raise BackupError("Database backup verification failed")
```

### Data Validation and Integrity

```python
# Data validation during migration
class MigrationValidator:
    def validate_pre_migration(self):
        """Validate data before migration"""
        validation_results = {
            'database_integrity': self.check_database_integrity(),
            'data_consistency': self.check_data_consistency(),
            'schema_version': self.check_schema_version(),
            'disk_space': self.check_disk_space()
        }
        
        if not all(validation_results.values()):
            raise ValidationError(f"Pre-migration validation failed: {validation_results}")
        
        return validation_results
    
    def validate_post_migration(self, phase):
        """Validate data after migration"""
        validation_results = {
            'record_count': self.verify_record_count(phase),
            'data_integrity': self.verify_data_integrity(phase),
            'encryption_status': self.verify_encryption_status(phase),
            'performance': self.verify_performance(phase)
        }
        
        return validation_results
```

---

## Compatibility Considerations

### Version Compatibility Matrix

| Component | Pre-Migration | Phase 1 | Phase 2 | Phase 3 | Notes |
|-----------|---------------|---------|---------|---------|-------|
| **Database Schema** | v0.x | v1.0 | v2.0 | v3.0 | Forward compatible |
| **API Interface** | Basic | Enhanced | Extended | Complete | Backward compatible |
| **Configuration** | Simple | Secure | Advanced | Full | Migration required |
| **Client Libraries** | v1.x | v2.x | v2.x | v3.x | Update recommended |

### Breaking Changes

**Phase 1 Breaking Changes:**
- Directory paths now encrypted (API unchanged)
- Database schema modified (migration handles)
- Configuration format enhanced

**Phase 2 Breaking Changes:**
- PII detection may flag previously accessible directories
- Permission system may restrict some operations
- Performance characteristics changed

**Phase 3 Breaking Changes:**
- All operations now logged (may impact performance)
- Security events may trigger alerts
- Audit requirements may affect data retention

### Compatibility Shims

```python
# Compatibility layer for legacy applications
class LegacyCompatibilityLayer:
    def __init__(self, security_manager):
        self.security_manager = security_manager
        self.legacy_api = LegacyDirectoryAPI()
    
    def get_directory(self, user_id, directory_id):
        """Legacy method with new security backend"""
        # Convert legacy call to new security API
        result = self.security_manager.retrieve_directory_preference(
            user_id, directory_id
        )
        
        if result.success:
            # Convert to legacy format
            return self.legacy_api.format_response(result.decrypted_path)
        else:
            # Handle security failures transparently
            return self.legacy_api.handle_error(result.error_message)
    
    def store_directory(self, user_id, directory_path):
        """Legacy storage with new security features"""
        # Apply new security features transparently
        result = self.security_manager.store_directory_preference(
            user_id, "legacy_tool", "general", directory_path
        )
        
        return self.legacy_api.format_storage_response(result)
```

---

## Post-Migration Verification

### Automated Verification Suite

```python
# Comprehensive post-migration verification
class PostMigrationVerification:
    def __init__(self, migration_phase):
        self.phase = migration_phase
        self.verifier = self.get_phase_verifier()
    
    def run_full_verification(self):
        """Run complete verification suite"""
        verification_results = {}
        
        # Core functionality tests
        verification_results['core_tests'] = self.run_core_tests()
        
        # Security feature tests
        verification_results['security_tests'] = self.run_security_tests()
        
        # Performance tests
        verification_results['performance_tests'] = self.run_performance_tests()
        
        # Data integrity tests
        verification_results['integrity_tests'] = self.run_integrity_tests()
        
        # Generate verification report
        return self.generate_verification_report(verification_results)
    
    def run_core_tests(self):
        """Test core functionality"""
        tests = [
            self.test_directory_storage,
            self.test_directory_retrieval,
            self.test_directory_listing,
            self.test_directory_deletion
        ]
        
        results = {}
        for test in tests:
            try:
                results[test.__name__] = test()
            except Exception as e:
                results[test.__name__] = {'success': False, 'error': str(e)}
        
        return results
```

### Manual Verification Checklist

**Phase 1 Verification:**
- [ ] All existing directories accessible
- [ ] New directories encrypted properly
- [ ] Decryption working correctly
- [ ] Performance within acceptable limits
- [ ] No data loss occurred

**Phase 2 Verification:**
- [ ] PII detection functioning
- [ ] Permission system operational
- [ ] PII-sensitive directories protected
- [ ] User access patterns working
- [ ] Backward compatibility maintained

**Phase 3 Verification:**
- [ ] Audit logging capturing all operations
- [ ] Security events being detected
- [ ] Historical data migrated correctly
- [ ] Monitoring and alerting functional
- [ ] Performance impact acceptable

---

## Rollback Procedures

### Automated Rollback

```python
# Automated rollback system
class MigrationRollback:
    def __init__(self, backup_manager):
        self.backup_manager = backup_manager
        self.rollback_log = []
    
    def rollback_phase(self, phase_number):
        """Rollback specific migration phase"""
        try:
            # Stop application services
            self.stop_services()
            
            # Restore database backup
            self.restore_database_backup(phase_number)
            
            # Restore configuration
            self.restore_configuration_backup(phase_number)
            
            # Verify rollback
            self.verify_rollback(phase_number)
            
            # Restart services
            self.start_services()
            
            return RollbackResult(
                success=True,
                phase=phase_number,
                restored_records=self.count_restored_records()
            )
            
        except Exception as e:
            self.rollback_log.append(f"Rollback failed: {e}")
            raise RollbackError(f"Failed to rollback phase {phase_number}: {e}")
    
    def emergency_rollback(self):
        """Emergency rollback to pre-migration state"""
        # Restore from most recent full backup
        return self.restore_full_backup()
```

### Manual Rollback Steps

```sql
-- Manual rollback example (Phase 1 to pre-migration)
BEGIN TRANSACTION;

-- Restore original table structure
CREATE TABLE directories_original AS 
SELECT 
    id,
    user_id,
    tool_id,
    category,
    -- Decrypt paths back to original format
    decrypt_path(encrypted_path, salt, nonce, user_id) as directory_path,
    created_at
FROM directories
WHERE decryption_successful = 1;

-- Verify record count matches
SELECT 
    (SELECT COUNT(*) FROM directories) as encrypted_count,
    (SELECT COUNT(*) FROM directories_original) as decrypted_count;

-- Replace tables if verification passes
DROP TABLE directories;
ALTER TABLE directories_original RENAME TO directories;

COMMIT;
```

---

## Troubleshooting

### Common Migration Issues

**Issue: Migration Timeout**
```bash
# Symptoms
Migration stuck at "Applying Phase 2 migrations..."
Process running for >2 hours

# Solutions
1. Check available disk space
2. Verify database locks
3. Increase migration timeout
4. Run migration in smaller batches

# Commands
python -m rfu.migration.diagnostics --check-locks
python -m rfu.migration.migration_manager --batch-size=500 --timeout=7200
```

**Issue: Encryption Failure**
```bash
# Symptoms
"EncryptionError: Failed to encrypt directory path"
Some directories not migrated

# Solutions
1. Verify cryptography library installation
2. Check available memory
3. Validate input data encoding
4. Retry with error recovery

# Commands
pip install --upgrade cryptography
python -m rfu.migration.encryption_recovery --retry-failed
```

**Issue: PII Detection Performance**
```bash
# Symptoms
Phase 2 migration extremely slow
High CPU usage during PII scanning

# Solutions
1. Reduce PII detection rules
2. Increase batch processing
3. Skip PII detection for large datasets
4. Use parallel processing

# Commands
python -m rfu.migration.pii_migration --fast-mode
python -m rfu.migration.pii_migration --parallel-workers=4
```

### Migration Diagnostics

```python
# Diagnostic tools
class MigrationDiagnostics:
    def run_full_diagnostics(self):
        """Run comprehensive migration diagnostics"""
        diagnostics = {
            'system': self.check_system_requirements(),
            'database': self.check_database_health(),
            'dependencies': self.check_dependencies(),
            'permissions': self.check_file_permissions(),
            'resources': self.check_system_resources()
        }
        
        return self.generate_diagnostic_report(diagnostics)
    
    def check_migration_readiness(self):
        """Check if system is ready for migration"""
        checks = [
            ('Database accessible', self.check_database_access),
            ('Sufficient disk space', self.check_disk_space),
            ('Required dependencies', self.check_dependencies),
            ('Backup location writable', self.check_backup_permissions),
            ('Migration scripts present', self.check_migration_scripts)
        ]
        
        for check_name, check_func in checks:
            result = check_func()
            if not result:
                raise MigrationReadinessError(f"Failed: {check_name}")
        
        return True
```

### Performance Optimization

```python
# Migration performance optimization
class MigrationOptimizer:
    def optimize_for_large_dataset(self, record_count):
        """Optimize migration for large datasets"""
        if record_count > 100000:
            return {
                'batch_size': 5000,
                'parallel_workers': 4,
                'memory_limit': '2GB',
                'checkpoint_interval': 10000
            }
        elif record_count > 10000:
            return {
                'batch_size': 1000,
                'parallel_workers': 2,
                'memory_limit': '1GB',
                'checkpoint_interval': 5000
            }
        else:
            return {
                'batch_size': 500,
                'parallel_workers': 1,
                'memory_limit': '512MB',
                'checkpoint_interval': 1000
            }
```

---

## Support and Resources

### Migration Support Contacts

- **Technical Support:** migration-support@rfu-hub.com
- **Emergency Rollback:** emergency-rollback@rfu-hub.com
- **Documentation:** docs@rfu-hub.com

### Additional Resources

- **API Documentation:** `docs/api_documentation.md`
- **Database Schema:** `docs/database_schema_documentation.md`
- **Security Configuration:** `docs/security_configuration_guide.md`
- **Troubleshooting Guide:** `docs/troubleshooting_guide.md`

### Migration Logs and Monitoring

```bash
# View migration logs
tail -f /var/log/rfu/migration.log

# Monitor migration progress
python -m rfu.migration.monitor --live

# Check migration status
python -m rfu.migration.status --all-phases
```

---

## Version Information

- **Migration Guide Version:** 1.0.0
- **Supported Migrations:** Phase 1-3
- **Target Schema Version:** 008
- **Minimum RFU Version:** 2.0.0

---

**Last Updated:** 2024  
**Migration Guide Version:** 1.0.0  
**Compatibility:** RFU Hub Security Framework v2.0+