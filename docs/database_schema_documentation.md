# RFU Hub Security Framework - Database Schema Documentation

## Overview

This document provides comprehensive documentation of the database schema for the RFU Hub Security Framework, covering all tables, indexes, views, triggers, and relationships implemented across Phases 1-3 of the security enhancement project.

## Table of Contents

1. [Schema Overview](#schema-overview)
2. [Core Tables](#core-tables)
3. [Security Tables](#security-tables)
4. [Audit Tables](#audit-tables)
5. [Migration History](#migration-history)
6. [Indexes and Performance](#indexes-and-performance)
7. [Views and Functions](#views-and-functions)
8. [Triggers and Constraints](#triggers-and-constraints)
9. [Data Relationships](#data-relationships)
10. [Security Considerations](#security-considerations)

---

## Schema Overview

The RFU Hub database schema is designed with security, performance, and scalability in mind. The schema supports:

- **Encrypted directory preference storage**
- **Comprehensive audit logging**
- **Role-based permission management**
- **PII detection and classification**
- **Performance optimization through strategic indexing**

### Database Engine
- **Primary:** SQLite 3.35+
- **File Format:** Single-file database with WAL mode
- **Encoding:** UTF-8
- **Page Size:** 4096 bytes (optimized for performance)

### Schema Version Management
- Migration-based versioning system
- Backward compatibility maintenance
- Rollback support for critical migrations
- Schema validation and integrity checks

---

## Core Tables

### 1. `directories`

Primary table for storing encrypted directory preferences.

```sql
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
    pii_sensitive BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);
```

**Field Descriptions:**

- `id`: Primary key, auto-incrementing identifier
- `user_id`: User identifier (FK reference, not enforced for flexibility)
- `tool_id`: Application/tool identifier requesting storage
- `category`: Directory category for organization
- `path_hash`: SHA-256 hash of original directory path (unique index)
- `encrypted_path`: AES-256-GCM encrypted directory path
- `salt`: 32-byte random salt for key derivation
- `nonce`: 12-byte random nonce for encryption
- `integrity_hash`: HMAC-SHA256 for data integrity verification
- `pii_sensitive`: Flag indicating if PII was detected in path
- `created_at`: Record creation timestamp
- `updated_at`: Last modification timestamp
- `last_accessed`: Last access timestamp for usage tracking
- `access_count`: Number of times directory has been accessed
- `is_active`: Soft delete flag for data retention

**Security Features:**
- All sensitive path data encrypted at rest
- Unique path hashing prevents duplicate storage
- Integrity verification for tamper detection
- PII classification for enhanced security

### 2. `directory_metadata`

Extended metadata for directory preferences.

```sql
CREATE TABLE directory_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    directory_id INTEGER NOT NULL,
    metadata_key TEXT NOT NULL,
    metadata_value TEXT,
    encrypted_value BLOB,
    is_encrypted BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (directory_id) REFERENCES directories(id) ON DELETE CASCADE,
    UNIQUE(directory_id, metadata_key)
);
```

**Field Descriptions:**

- `directory_id`: Foreign key to directories table
- `metadata_key`: Metadata attribute name
- `metadata_value`: Plain text metadata value (for non-sensitive data)
- `encrypted_value`: Encrypted metadata value (for sensitive data)
- `is_encrypted`: Flag indicating encryption status

**Use Cases:**
- Custom directory attributes
- Tool-specific configuration
- Performance metrics
- User preferences

---

## Security Tables

### 3. `directory_permissions`

Role-based access control for directory preferences.

```sql
CREATE TABLE directory_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    permission_type TEXT NOT NULL,
    granted BOOLEAN DEFAULT FALSE,
    granted_by TEXT,
    granted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(user_id, resource_id, permission_type)
);
```

**Permission Types:**
- `read`: View directory preference
- `write`: Modify directory preference
- `execute`: Use directory in applications
- `share`: Share with other users
- `delete`: Remove directory preference
- `admin`: Full administrative access

**Field Descriptions:**

- `resource_id`: Directory path hash or pattern
- `permission_type`: Type of permission granted
- `granted`: Whether permission is active
- `granted_by`: User who granted the permission
- `expires_at`: Optional permission expiration
- `is_active`: Active permission flag

### 4. `encryption_keys`

Key management for directory encryption (metadata only).

```sql
CREATE TABLE encryption_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_id TEXT UNIQUE NOT NULL,
    user_id TEXT NOT NULL,
    algorithm TEXT DEFAULT 'AES-256-GCM',
    key_derivation TEXT DEFAULT 'PBKDF2-HMAC-SHA256',
    iterations INTEGER DEFAULT 100000,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

**Security Note:** Actual encryption keys are never stored. This table contains only metadata about key derivation parameters.

### 5. `pii_detections`

PII detection results and classifications.

```sql
CREATE TABLE pii_detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    directory_id INTEGER NOT NULL,
    pii_type TEXT NOT NULL,
    confidence_score REAL NOT NULL,
    detected_pattern TEXT,
    location_info TEXT,
    detection_method TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (directory_id) REFERENCES directories(id) ON DELETE CASCADE
);
```

**PII Types:**
- `personal_name`: Names in directory paths
- `ssn`: Social Security Numbers
- `credit_card`: Credit card numbers
- `email`: Email addresses
- `phone`: Phone numbers
- `date_of_birth`: Birth date patterns
- `medical_record`: Medical information indicators
- `financial`: Financial data indicators

---

## Audit Tables

### 6. `audit_logs`

Comprehensive audit logging for all directory operations.

```sql
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id TEXT NOT NULL,
    resource_id TEXT,
    operation_type TEXT NOT NULL,
    operation_result TEXT NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    session_id TEXT,
    request_metadata TEXT, -- JSON
    response_metadata TEXT, -- JSON
    duration_ms INTEGER,
    error_message TEXT
);
```

**Operation Types:**
- `create`: Directory creation
- `read`: Directory retrieval
- `update`: Directory modification
- `delete`: Directory deletion
- `permission_change`: Permission modifications
- `share`: Sharing operations
- `encrypt`: Encryption operations
- `decrypt`: Decryption operations

**Operation Results:**
- `success`: Operation completed successfully
- `failure`: Operation failed
- `partial`: Partial success with warnings
- `denied`: Permission denied

### 7. `security_events`

Security-specific event logging.

```sql
CREATE TABLE security_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    event_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    user_id TEXT,
    source_ip TEXT,
    event_details TEXT, -- JSON
    resolution_status TEXT DEFAULT 'open',
    resolved_at DATETIME,
    resolved_by TEXT
);
```

**Event Types:**
- `authentication_failure`: Failed login attempts
- `encryption_failure`: Encryption failures
- `permission_violation`: Unauthorized access
- `pii_exposure`: Potential PII exposure
- `suspicious_activity`: Unusual patterns
- `data_breach_attempt`: Potential breaches

**Severity Levels:**
- `low`: Informational events
- `medium`: Warning events
- `high`: Security concerns
- `critical`: Immediate attention required

---

## Migration History

### 8. `schema_migrations`

Database migration tracking and versioning.

```sql
CREATE TABLE schema_migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL,
    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    execution_time_ms INTEGER,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    checksum TEXT,
    rollback_sql TEXT
);
```

### Migration Timeline

| Version | Description | Phase | Applied |
|---------|-------------|-------|---------|
| `001_initial_schema` | Basic directory storage | Phase 1 | ✅ |
| `002_encryption_support` | Add encryption fields | Phase 1 | ✅ |
| `003_pii_detection` | PII detection tables | Phase 2 | ✅ |
| `004_permissions_rbac` | Permission management | Phase 2 | ✅ |
| `005_audit_logging` | Comprehensive auditing | Phase 3 | ✅ |
| `006_security_events` | Security event tracking | Phase 3 | ✅ |
| `007_performance_indexes` | Performance optimization | Phase 3 | ✅ |
| `008_metadata_tables` | Extended metadata support | Phase 3 | ✅ |

---

## Indexes and Performance

### Primary Indexes

```sql
-- Core performance indexes
CREATE INDEX idx_directories_user_id ON directories(user_id);
CREATE INDEX idx_directories_path_hash ON directories(path_hash);
CREATE INDEX idx_directories_tool_id ON directories(tool_id);
CREATE INDEX idx_directories_category ON directories(category);
CREATE INDEX idx_directories_created_at ON directories(created_at);
CREATE INDEX idx_directories_pii_sensitive ON directories(pii_sensitive);

-- Permission indexes
CREATE INDEX idx_permissions_user_resource ON directory_permissions(user_id, resource_id);
CREATE INDEX idx_permissions_resource ON directory_permissions(resource_id);
CREATE INDEX idx_permissions_type ON directory_permissions(permission_type);

-- Audit indexes
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_logs_operation_type ON audit_logs(operation_type);
CREATE INDEX idx_audit_logs_resource_id ON audit_logs(resource_id);

-- Security event indexes
CREATE INDEX idx_security_events_timestamp ON security_events(timestamp);
CREATE INDEX idx_security_events_severity ON security_events(severity);
CREATE INDEX idx_security_events_event_type ON security_events(event_type);
CREATE INDEX idx_security_events_user_id ON security_events(user_id);
```

### Composite Indexes

```sql
-- Composite indexes for complex queries
CREATE INDEX idx_directories_user_tool ON directories(user_id, tool_id);
CREATE INDEX idx_directories_active_created ON directories(is_active, created_at);
CREATE INDEX idx_permissions_active_user ON directory_permissions(is_active, user_id);
CREATE INDEX idx_audit_logs_user_timestamp ON audit_logs(user_id, timestamp);
```

### Performance Metrics

- **Query Performance Target:** <100ms for standard operations
- **Index Maintenance:** Automatic with minimal overhead
- **Storage Overhead:** <5% increase from base tables
- **Concurrent Access:** Optimized for multi-user environments

---

## Views and Functions

### Security Views

```sql
-- Active directory view (excludes deleted records)
CREATE VIEW active_directories AS
SELECT 
    d.*,
    COUNT(p.id) as permission_count,
    MAX(p.granted_at) as last_permission_change
FROM directories d
LEFT JOIN directory_permissions p ON d.path_hash = p.resource_id
WHERE d.is_active = TRUE
GROUP BY d.id;

-- User security summary
CREATE VIEW user_security_summary AS
SELECT 
    user_id,
    COUNT(*) as total_directories,
    COUNT(CASE WHEN pii_sensitive = TRUE THEN 1 END) as pii_directories,
    MAX(created_at) as last_directory_added,
    AVG(access_count) as avg_access_count
FROM directories
WHERE is_active = TRUE
GROUP BY user_id;

-- Recent security events
CREATE VIEW recent_security_events AS
SELECT *
FROM security_events
WHERE timestamp >= datetime('now', '-7 days')
ORDER BY timestamp DESC;
```

### Audit Views

```sql
-- Failed operations summary
CREATE VIEW failed_operations AS
SELECT 
    operation_type,
    user_id,
    COUNT(*) as failure_count,
    MAX(timestamp) as last_failure
FROM audit_logs
WHERE operation_result = 'failure'
    AND timestamp >= datetime('now', '-24 hours')
GROUP BY operation_type, user_id
ORDER BY failure_count DESC;

-- High-severity events
CREATE VIEW critical_security_events AS
SELECT *
FROM security_events
WHERE severity IN ('high', 'critical')
    AND resolution_status = 'open'
ORDER BY timestamp DESC;
```

---

## Triggers and Constraints

### Update Triggers

```sql
-- Update timestamp trigger for directories
CREATE TRIGGER update_directories_timestamp
    AFTER UPDATE ON directories
    FOR EACH ROW
BEGIN
    UPDATE directories 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE id = NEW.id;
END;

-- Access tracking trigger
CREATE TRIGGER track_directory_access
    AFTER UPDATE OF last_accessed ON directories
    FOR EACH ROW
BEGIN
    UPDATE directories 
    SET access_count = access_count + 1 
    WHERE id = NEW.id;
END;
```

### Security Triggers

```sql
-- Log permission changes
CREATE TRIGGER log_permission_changes
    AFTER INSERT OR UPDATE OR DELETE ON directory_permissions
    FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (
        user_id, 
        resource_id, 
        operation_type, 
        operation_result,
        request_metadata
    ) VALUES (
        COALESCE(NEW.user_id, OLD.user_id),
        COALESCE(NEW.resource_id, OLD.resource_id),
        'permission_change',
        'success',
        json_object(
            'action', CASE 
                WHEN OLD.id IS NULL THEN 'grant'
                WHEN NEW.id IS NULL THEN 'revoke'
                ELSE 'modify'
            END,
            'permission_type', COALESCE(NEW.permission_type, OLD.permission_type)
        )
    );
END;

-- Detect suspicious activities
CREATE TRIGGER detect_suspicious_activity
    AFTER INSERT ON audit_logs
    FOR EACH ROW
    WHEN NEW.operation_result = 'failure'
BEGIN
    INSERT INTO security_events (
        event_type,
        severity,
        user_id,
        event_details
    )
    SELECT 
        'suspicious_activity',
        CASE 
            WHEN failure_count >= 5 THEN 'high'
            WHEN failure_count >= 3 THEN 'medium'
            ELSE 'low'
        END,
        NEW.user_id,
        json_object(
            'operation_type', NEW.operation_type,
            'failure_count', failure_count,
            'time_window', '1 hour'
        )
    FROM (
        SELECT COUNT(*) as failure_count
        FROM audit_logs
        WHERE user_id = NEW.user_id
            AND operation_result = 'failure'
            AND timestamp >= datetime('now', '-1 hour')
    )
    WHERE failure_count >= 3;
END;
```

### Data Constraints

```sql
-- Ensure valid permission types
CREATE TABLE permission_types (
    type_name TEXT PRIMARY KEY,
    description TEXT NOT NULL
);

INSERT INTO permission_types VALUES 
    ('read', 'View directory preference'),
    ('write', 'Modify directory preference'),
    ('execute', 'Use directory in applications'),
    ('share', 'Share with other users'),
    ('delete', 'Remove directory preference'),
    ('admin', 'Full administrative access');

-- Foreign key constraint (if using PRAGMA foreign_keys=ON)
ALTER TABLE directory_permissions 
ADD CONSTRAINT fk_permission_type 
FOREIGN KEY (permission_type) 
REFERENCES permission_types(type_name);
```

---

## Data Relationships

### Entity Relationship Diagram

```
directories (1) ─────→ (N) directory_metadata
    │
    │ (1)
    │
    ↓ (N)
pii_detections

directories (1) ─────→ (N) audit_logs
    │                         ↑
    │ (path_hash)             │
    │                         │
    ↓ (resource_id)           │
directory_permissions ────────┘

security_events (standalone audit table)

schema_migrations (system table)
```

### Relationship Details

1. **One-to-Many Relationships:**
   - `directories` → `directory_metadata` (extended attributes)
   - `directories` → `pii_detections` (PII findings)
   - `directories` → `audit_logs` (via path_hash/resource_id)

2. **Independent Tables:**
   - `directory_permissions` (linked by resource_id/path_hash)
   - `security_events` (system-wide security events)
   - `encryption_keys` (key metadata only)
   - `schema_migrations` (version control)

3. **Referential Integrity:**
   - Cascading deletes for dependent data
   - Soft deletes for audit trail preservation
   - Foreign key constraints where appropriate

---

## Security Considerations

### Data Protection

1. **Encryption at Rest:**
   - All sensitive directory paths encrypted with AES-256-GCM
   - User-specific key derivation with PBKDF2
   - Salt and nonce uniqueness guaranteed

2. **Integrity Protection:**
   - HMAC-SHA256 verification for all encrypted data
   - Tamper detection through integrity hashes
   - Audit trail immutability

3. **Access Control:**
   - Role-based permission system
   - Granular permission types
   - Permission expiration support

### Privacy Protection

1. **PII Handling:**
   - Automatic PII detection and classification
   - Enhanced security for PII-sensitive paths
   - Compliance with privacy regulations

2. **Data Minimization:**
   - Only necessary data stored
   - Regular cleanup of expired data
   - Configurable retention policies

3. **Audit and Monitoring:**
   - Comprehensive audit logging
   - Security event detection
   - Anomaly detection triggers

### Performance Security

1. **Query Optimization:**
   - Strategic indexing for common queries
   - Parameterized queries to prevent SQL injection
   - Connection pooling for scalability

2. **Resource Management:**
   - Database size monitoring (<5% growth target)
   - Query performance targets (<100ms)
   - Concurrent access optimization

3. **Backup and Recovery:**
   - Regular automated backups
   - Point-in-time recovery capability
   - Disaster recovery procedures

---

## Database Maintenance

### Regular Maintenance Tasks

```sql
-- Analyze table statistics
ANALYZE;

-- Vacuum database (reclaim space)
VACUUM;

-- Integrity check
PRAGMA integrity_check;

-- Update table statistics
PRAGMA optimize;
```

### Monitoring Queries

```sql
-- Database size monitoring
SELECT 
    page_count * page_size / 1024 / 1024 as size_mb,
    page_count,
    page_size
FROM pragma_page_count(), pragma_page_size();

-- Performance monitoring
SELECT 
    sql,
    executions,
    total_time_ms,
    avg_time_ms
FROM (
    SELECT 
        sql,
        COUNT(*) as executions,
        SUM(duration_ms) as total_time_ms,
        AVG(duration_ms) as avg_time_ms
    FROM audit_logs 
    WHERE timestamp >= datetime('now', '-1 day')
        AND duration_ms IS NOT NULL
    GROUP BY sql
) ORDER BY total_time_ms DESC;
```

---

## Version Information

- **Schema Version:** 008 (Latest)
- **Database Engine:** SQLite 3.35+
- **Character Set:** UTF-8
- **Collation:** BINARY (case-sensitive)
- **Page Size:** 4096 bytes
- **Journal Mode:** WAL (Write-Ahead Logging)

---

## Support and Maintenance

For database schema questions, migration issues, or performance concerns, please refer to the migration guide and troubleshooting documentation.

**Last Updated:** 2024  
**Schema Version:** 008  
**Documentation Version:** 1.0.0