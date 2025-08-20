# Phase 3 Directory Security Implementation Documentation

## Overview

This document provides comprehensive documentation for Phase 3 of the RFU Hub Preferences Security Implementation, focusing on Directory Preferences Security Controls and PII Protection. Phase 3 builds upon the foundation established in Phases 1 and 2 to create a robust security framework for managing directory preferences with advanced PII detection, encryption, and audit capabilities.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
3. [Security Features](#security-features)
4. [Database Schema](#database-schema)
5. [API Documentation](#api-documentation)
6. [User Interface](#user-interface)
7. [Security Guidelines](#security-guidelines)
8. [Configuration](#configuration)
9. [Testing](#testing)
10. [Deployment](#deployment)
11. [Troubleshooting](#troubleshooting)

## Architecture Overview

Phase 3 implements a comprehensive directory security system with the following architectural principles:

### Security-First Design
- **Defense in Depth**: Multiple layers of security validation
- **Principle of Least Privilege**: Role-based access control
- **Data Protection**: End-to-end encryption for sensitive paths
- **Audit Trail**: Comprehensive logging for compliance

### Component Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   DirectorySecurityGUI                     │
│                    (User Interface)                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│              DirectorySecurityManager                      │
│               (Central Coordinator)                        │
└─────┬─────┬─────┬─────┬─────┬─────┬─────────────────────────┘
      │     │     │     │     │     │
      ▼     ▼     ▼     ▼     ▼     ▼
┌─────────┐ ┌───────┐ ┌──────┐ ┌──────┐ ┌─────────┐ ┌──────────┐
│Path     │ │PII    │ │Path  │ │Dir   │ │Dir      │ │Dir       │
│Validator│ │Detector│ │Encr  │ │Perms │ │Audit    │ │Database  │
│         │ │       │ │yption│ │      │ │Logger   │ │Manager   │
└─────────┘ └───────┘ └──────┘ └──────┘ └─────────┘ └──────────┘
```

### Data Flow

1. **Directory Input** → Path Validation → PII Detection
2. **Security Analysis** → Encryption Decision → Permission Check
3. **Secure Storage** → Audit Logging → Database Storage
4. **Retrieval** → Decryption → Access Validation → Audit Log

## Core Components

### 1. DirectorySecurityManager

**File**: `src/rfu/core/directory_security/directory_security_manager.py`

Central coordinator for all directory security operations.

#### Key Features
- Integrated PII protection and encryption decisions
- Comprehensive security validation pipeline
- Audit logging for all operations
- Permission-based access control
- Secure path hashing for database indexing

#### Main Methods
```python
def store_directory_preference(user_id: str, tool_name: str, 
                             directory_type: str, directory_path: str) -> DirectoryStorageResult
def retrieve_directory_preference(user_id: str, path_hash: str) -> DirectoryRetrievalResult
def list_user_directories(user_id: str, tool_name: str = None, 
                         directory_type: str = None) -> List[Dict]
def delete_directory_preference(user_id: str, path_hash: str) -> bool
```

### 2. DirectoryPathValidator

**File**: `src/rfu/core/directory_security/directory_validator.py`

Comprehensive path validation with security focus.

#### Security Validations
- **Path Traversal Protection**: Prevents `../` attacks
- **Symbolic Link Validation**: Checks for malicious symlinks
- **Character Validation**: Removes dangerous characters
- **Length Limits**: Prevents buffer overflow attacks
- **Network Path Security**: Validates UNC and network paths

#### Usage Example
```python
validator = DirectoryPathValidator()
result = validator.validate_directory_path("/path/to/directory", "user123")
if result.valid:
    print(f"Safe path: {result.normalized_path}")
else:
    print(f"Security issue: {result.reason}")
```

### 3. PathSanitizer

**File**: `src/rfu/core/directory_security/path_sanitizer.py`

Path sanitization and anonymization for security and privacy.

#### Features
- **Character Sanitization**: Removes/replaces dangerous characters
- **Path Anonymization**: Replaces PII with placeholders
- **Display Sanitization**: Safe path display for UI
- **Logging Sanitization**: Anonymized paths for logs

#### Sanitization Rules
```python
# Character replacement rules
DANGEROUS_CHARS = ['<', '>', '|', '*', '?', '"', '\x00']
REPLACEMENT_CHAR = '_'

# Anonymization patterns
USER_PATTERNS = [r'[Uu]sers[/\\]([^/\\]+)', r'[Hh]ome[/\\]([^/\\]+)']
REPLACEMENT = '[USER]'
```

### 4. PIIDetector

**File**: `src/rfu/core/directory_security/pii_detector.py`

Advanced PII detection with 5-level sensitivity scoring.

#### Detection Patterns
- **Username Directories**: `/Users/john.doe/`, `/home/username/`
- **Personal Documents**: `Documents/Personal/`, `My Documents/`
- **Financial Directories**: `Financial/`, `TaxReturns/`, `Banking/`
- **Medical Records**: `Medical/`, `Health/`, `Doctor/`
- **Security Directories**: `.ssh/`, `certificates/`, `keys/`

#### Sensitivity Levels
1. **Level 1**: Public/system directories
2. **Level 2**: User workspace directories
3. **Level 3**: Personal document directories
4. **Level 4**: Financial/medical directories
5. **Level 5**: Security/credential directories

### 5. DirectoryPathEncryption

**File**: `src/rfu/core/directory_security/directory_encryption.py`

Enterprise-grade encryption using AES-256-GCM.

#### Encryption Specifications
- **Algorithm**: AES-256-GCM for authenticated encryption
- **Key Derivation**: PBKDF2-SHA256 with 100,000 iterations
- **Salt**: 32-byte random salt per encryption
- **Nonce**: 12-byte random nonce for GCM mode
- **Integrity**: Built-in integrity verification

#### Security Features
```python
# User-specific key derivation
def _derive_directory_key(self, user_id: str, salt: bytes) -> bytes:
    return PBKDF2(
        password=user_id.encode('utf-8'),
        salt=salt,
        dkLen=32,  # 256-bit key
        count=100000,  # 100k iterations
        prf=lambda p, s: hmac.new(p, s, hashlib.sha256).digest()
    )
```

### 6. DirectoryPermissionManager

**File**: `src/rfu/core/directory_security/directory_permissions.py`

Role-based access control with hierarchical permissions.

#### Role Hierarchy
```python
class DirectoryRole(Enum):
    GUEST = "guest"           # Read-only access
    USER = "user"             # Read/write own data
    POWER_USER = "power_user" # Enhanced operations
    ADMIN = "admin"           # Full administrative access
    SYSTEM = "system"         # System-level operations
```

#### Permission Levels
```python
class PermissionLevel(Enum):
    NONE = 0     # No access
    READ = 1     # Read access
    WRITE = 2    # Read/write access  
    DELETE = 3   # Read/write/delete access
    ADMIN = 4    # Administrative access
```

### 7. DirectoryAuditLogger

**File**: `src/rfu/core/directory_security/directory_audit.py`

Comprehensive audit logging with anonymization.

#### Audit Event Types
- **DIRECTORY_OPERATION**: Store/retrieve/delete operations
- **ACCESS_DENIED**: Permission violations
- **SECURITY_VIOLATION**: Security policy violations
- **PII_DETECTION**: PII detection events
- **ENCRYPTION_EVENT**: Encryption/decryption events

#### Compliance Features
- **Data Anonymization**: PII removal from audit logs
- **Retention Policies**: Configurable log retention
- **Integrity Protection**: Tamper-evident logging
- **Compliance Reporting**: Pre-built compliance reports

## Security Features

### PII Protection

#### Automatic Detection
The system automatically detects PII in directory paths using pattern matching:

```python
# Example PII detection patterns
USERNAME_PATTERNS = [
    r'[Uu]sers[/\\]([a-zA-Z0-9._-]+)',
    r'[Hh]ome[/\\]([a-zA-Z0-9._-]+)',
    r'[Pp]rofiles[/\\]([a-zA-Z0-9._-]+)'
]

PERSONAL_PATTERNS = [
    r'[Dd]ocuments[/\\][Pp]ersonal',
    r'[Mm]y [Dd]ocuments',
    r'[Pp]rivate',
    r'[Cc]onfidential'
]
```

#### Encryption Decisions
Paths are automatically encrypted based on sensitivity analysis:

```python
def _should_encrypt_path(self, pii_result: PIIAnalysisResult) -> bool:
    return (pii_result.sensitivity_level >= 3 or 
            pii_result.requires_encryption or
            len(pii_result.pii_indicators) >= 2)
```

### Access Control

#### Role-Based Permissions
Access control is enforced through role hierarchy:

```python
ROLE_HIERARCHY = {
    DirectoryRole.GUEST: 1,
    DirectoryRole.USER: 2,
    DirectoryRole.POWER_USER: 3,
    DirectoryRole.ADMIN: 4,
    DirectoryRole.SYSTEM: 5
}
```

#### Permission Enforcement
```python
def check_directory_permission(self, user_id: str, resource_path: str, 
                             action: str) -> PermissionCheckResult:
    user_role = self._get_user_role(user_id)
    required_level = self._get_required_permission_level(action)
    role_level = self._get_role_permission_level(user_role)
    
    authorized = role_level >= required_level
    return PermissionCheckResult(authorized, user_role, required_level)
```

### Audit Trail

#### Comprehensive Logging
All security-relevant events are logged:

```python
# Example audit log entry
{
    "event_id": "uuid-string",
    "event_type": "DIRECTORY_OPERATION",
    "severity": "INFO",
    "user_id": "user123",
    "resource_id": "path_hash",
    "action": "store",
    "success": true,
    "details": {
        "tool_name": "file_browser",
        "directory_type": "favorite",
        "pii_sensitive": true,
        "sensitivity_level": 4
    },
    "timestamp": "2024-01-01T12:00:00Z",
    "anonymized_data": {
        "sanitized_path": "/[USER]/[DOCS]/[PERSONAL]"
    }
}
```

## Database Schema

### Core Tables

#### secure_directories
Primary table for encrypted directory storage:

```sql
CREATE TABLE secure_directories (
    storage_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    directory_type TEXT NOT NULL,
    encrypted_path BLOB NOT NULL,
    path_hash TEXT NOT NULL UNIQUE,
    is_pii_sensitive BOOLEAN NOT NULL DEFAULT 0,
    sensitivity_level INTEGER NOT NULL DEFAULT 1,
    encryption_metadata TEXT,
    pii_indicators TEXT,
    metadata TEXT,
    created_at TEXT NOT NULL,
    last_accessed_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

#### directory_permissions
Access control and permissions:

```sql
CREATE TABLE directory_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    resource_path TEXT NOT NULL,
    permission_level INTEGER NOT NULL,
    role TEXT NOT NULL,
    granted_by TEXT NOT NULL,
    granted_at TEXT NOT NULL,
    expires_at TEXT,
    restrictions TEXT,
    active BOOLEAN NOT NULL DEFAULT 1
);
```

#### directory_audit_log
Comprehensive audit logging:

```sql
CREATE TABLE directory_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL UNIQUE,
    event_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    user_id TEXT NOT NULL,
    resource_id TEXT,
    action TEXT NOT NULL,
    success BOOLEAN NOT NULL,
    details TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    anonymized_data TEXT
);
```

### Security Views

#### security_monitoring_view
Real-time security monitoring:

```sql
CREATE VIEW security_monitoring_view AS
SELECT 
    dal.timestamp,
    dal.event_type,
    dal.severity,
    dal.user_id,
    dal.action,
    dal.success,
    CASE WHEN dal.event_type = 'SECURITY_VIOLATION' THEN 'HIGH'
         WHEN dal.event_type = 'ACCESS_DENIED' THEN 'MEDIUM'
         ELSE 'LOW' END as risk_level
FROM directory_audit_log dal
WHERE dal.timestamp >= datetime('now', '-24 hours')
ORDER BY dal.timestamp DESC;
```

## API Documentation

### DirectorySecurityManager API

#### store_directory_preference()
Securely store a directory preference with automatic PII detection and encryption.

**Parameters:**
- `user_id` (str): User identifier
- `tool_name` (str): Name of the tool/application
- `directory_type` (str): Type of directory (favorite, recent, etc.)
- `directory_path` (str): Full directory path

**Returns:**
- `DirectoryStorageResult`: Storage result with security metadata

**Example:**
```python
manager = DirectorySecurityManager(db_manager)
result = manager.store_directory_preference(
    "user123", 
    "file_browser", 
    "favorite", 
    "C:\\Users\\john\\Documents\\Personal"
)

if result.success:
    print(f"Stored with hash: {result.path_hash}")
    print(f"PII sensitive: {result.pii_sensitive}")
    print(f"Sensitivity level: {result.sensitivity_level}")
else:
    print(f"Failed: {result.error_message}")
```

#### retrieve_directory_preference()
Securely retrieve and decrypt a directory preference.

**Parameters:**
- `user_id` (str): User identifier
- `path_hash` (str): Unique path hash from storage

**Returns:**
- `DirectoryRetrievalResult`: Retrieval result with decrypted path

**Example:**
```python
result = manager.retrieve_directory_preference("user123", "hash_value")
if result.success:
    print(f"Directory: {result.directory_path}")
    print(f"Tool: {result.tool_name}")
else:
    print(f"Failed: {result.error_message}")
```

### PIIDetector API

#### analyze_directory_path()
Analyze a directory path for PII content and sensitivity.

**Parameters:**
- `directory_path` (str): Directory path to analyze

**Returns:**
- `PIIAnalysisResult`: Analysis result with PII indicators

**Example:**
```python
detector = PIIDetector()
result = detector.analyze_directory_path("/home/john.doe/Documents/Financial")

print(f"Contains PII: {result.contains_pii}")
print(f"Sensitivity Level: {result.sensitivity_level}")
print(f"PII Indicators: {result.pii_indicators}")
print(f"Anonymized Path: {result.anonymized_path}")
print(f"Requires Encryption: {result.requires_encryption}")
```

## User Interface

### DirectorySecurityGUI

The GUI component provides a user-friendly interface for managing secure directory preferences.

#### Main Features
- **Directory List**: Tree view with security indicators
- **Security Analysis**: Real-time PII detection and warnings
- **Filter Options**: Filter by security level, PII sensitivity, encryption status
- **Details Panel**: Comprehensive directory information
- **Security Settings**: Configurable security options

#### Security Indicators
- 🔴 **High Security**: Sensitivity level 4-5
- 🟡 **Medium Security**: Sensitivity level 2-3  
- 🟢 **Low Security**: Sensitivity level 1
- 🔐 **Encrypted**: Path is encrypted
- 👤 **PII Sensitive**: Contains personal information
- ⚠️ **Warnings**: Security warnings present

#### Usage Example
```python
# Create GUI widget
gui = DirectorySecurityGUI(parent_frame, db_manager, "user123", DirectoryRole.USER)

# The GUI automatically:
# - Loads user's directory preferences
# - Shows security analysis for each path
# - Provides add/remove functionality
# - Displays PII warnings and encryption status
```

## Security Guidelines

### Development Guidelines

#### Path Validation
1. **Always validate** user input before processing
2. **Sanitize paths** before storage or display
3. **Use normalized paths** for comparison operations
4. **Check file system permissions** before access

#### Encryption Practices
1. **Encrypt sensitive paths** automatically based on PII analysis
2. **Use strong encryption** (AES-256-GCM) with proper key derivation
3. **Protect encryption keys** with user-specific derivation
4. **Verify integrity** on decryption

#### Access Control
1. **Implement least privilege** principle
2. **Validate permissions** before every operation
3. **Use role-based access** control consistently
4. **Audit all access** attempts

### Operational Guidelines

#### User Data Protection
1. **Minimize PII exposure** in logs and displays
2. **Anonymize sensitive paths** for non-essential operations
3. **Implement data retention** policies
4. **Provide user control** over their data

#### Incident Response
1. **Monitor security events** through audit logs
2. **Investigate anomalies** promptly
3. **Maintain incident logs** for compliance
4. **Update security measures** based on threats

## Configuration

### Security Configuration

#### PII Detection Settings
```python
PII_DETECTION_CONFIG = {
    "enable_username_detection": True,
    "enable_personal_directory_detection": True,
    "enable_financial_directory_detection": True,
    "enable_medical_directory_detection": True,
    "sensitivity_threshold": 3,  # Auto-encrypt threshold
    "custom_patterns": []  # Additional PII patterns
}
```

#### Encryption Settings
```python
ENCRYPTION_CONFIG = {
    "algorithm": "AES-256-GCM",
    "key_derivation": "PBKDF2-SHA256",
    "iterations": 100000,
    "salt_length": 32,
    "nonce_length": 12,
    "auto_encrypt_threshold": 3
}
```

#### Audit Settings
```python
AUDIT_CONFIG = {
    "enable_audit_logging": True,
    "log_successful_operations": True,
    "log_failed_operations": True,
    "anonymize_audit_data": True,
    "retention_days": 365,
    "compliance_reporting": True
}
```

## Testing

### Test Coverage

The comprehensive test suite covers:

1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Component interaction testing
3. **Security Tests**: Vulnerability and penetration testing
4. **Performance Tests**: Encryption/decryption performance
5. **UI Tests**: GUI functionality testing

### Running Tests

```bash
# Run all Phase 3 security tests
python -m pytest tests/test_directory_security.py -v

# Run specific test class
python -m pytest tests/test_directory_security.py::TestDirectorySecurityManagerIntegration -v

# Run with coverage
python -m pytest tests/test_directory_security.py --cov=src/rfu/core/directory_security --cov-report=html
```

### Test Categories

#### Security Validation Tests
- Path traversal attack prevention
- Invalid character handling
- Malicious input rejection
- Permission bypass attempts

#### Encryption Tests
- Key derivation verification
- Encryption/decryption cycles
- Integrity verification
- User-specific encryption

#### PII Detection Tests
- Pattern recognition accuracy
- Sensitivity level calculation
- Anonymization effectiveness
- False positive/negative rates

## Deployment

### Database Migration

1. **Run Migration 004**:
   ```bash
   python src/rfu/database/migrations/004_secure_directory_schema.sql
   ```

2. **Verify Schema**:
   ```sql
   -- Check table creation
   SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'directory_%';
   
   -- Verify indexes
   SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_directory_%';
   ```

### Component Integration

1. **Initialize Security Manager**:
   ```python
   from rfu.core.directory_security import DirectorySecurityManager
   
   security_manager = DirectorySecurityManager(db_manager)
   ```

2. **Configure GUI Integration**:
   ```python
   from rfu.core.directory_security.directory_security_gui import create_directory_security_widget
   
   security_widget = create_directory_security_widget(
       parent_frame, db_manager, user_id, user_role
   )
   ```

### Performance Considerations

#### Encryption Performance
- **Key Derivation**: PBKDF2 with 100k iterations (~100ms)
- **Encryption**: AES-256-GCM (~1ms for typical paths)
- **Database Operations**: Indexed queries for fast retrieval

#### Memory Usage
- **Encryption Keys**: Temporary, cleared after use
- **PII Detection**: Pattern compilation cached
- **Audit Logs**: Configurable retention policies

## Troubleshooting

### Common Issues

#### Encryption Failures
**Symptom**: Directory storage fails with encryption errors
**Causes**: 
- Invalid user credentials
- Corrupted encryption metadata
- Key derivation failures

**Solutions**:
```python
# Debug encryption
try:
    result = encryption.encrypt_directory_path(path, user_id)
    if not result.success:
        logger.error(f"Encryption failed: {result.error_message}")
except Exception as e:
    logger.error(f"Encryption exception: {e}")
```

#### PII Detection Issues
**Symptom**: Incorrect PII sensitivity levels
**Causes**:
- Pattern mismatch
- Custom directory structures
- Non-standard naming conventions

**Solutions**:
```python
# Debug PII detection
detector = PIIDetector()
result = detector.analyze_directory_path(path)
logger.info(f"PII Analysis: {result}")
logger.info(f"Matched patterns: {result.pii_indicators}")
```

#### Permission Denied Errors
**Symptom**: Users cannot access their directory preferences
**Causes**:
- Incorrect role assignment
- Missing permissions
- Database constraint violations

**Solutions**:
```python
# Check user permissions
perm_manager = DirectoryPermissionManager(db_manager)
result = perm_manager.check_directory_permission(user_id, resource, action)
if not result.authorized:
    logger.warning(f"Access denied: {result.reason}")
```

### Performance Optimization

#### Database Optimization
1. **Index Usage**: Ensure proper indexing on frequently queried columns
2. **Query Optimization**: Use parameterized queries
3. **Connection Pooling**: Implement connection pooling for high load

#### Encryption Optimization
1. **Key Caching**: Cache derived keys temporarily
2. **Batch Operations**: Process multiple paths in batches
3. **Async Processing**: Use async operations for encryption

### Security Monitoring

#### Audit Log Analysis
```sql
-- Check for security violations
SELECT * FROM directory_audit_log 
WHERE event_type = 'SECURITY_VIOLATION' 
AND timestamp >= datetime('now', '-24 hours');

-- Monitor failed access attempts
SELECT user_id, COUNT(*) as failed_attempts 
FROM directory_audit_log 
WHERE event_type = 'ACCESS_DENIED' 
AND timestamp >= datetime('now', '-1 hour')
GROUP BY user_id 
HAVING COUNT(*) > 5;
```

#### Performance Monitoring
```python
# Monitor encryption performance
import time

start_time = time.time()
result = encryption.encrypt_directory_path(path, user_id)
encryption_time = time.time() - start_time

if encryption_time > 0.5:  # 500ms threshold
    logger.warning(f"Slow encryption: {encryption_time:.2f}s for {path}")
```

## Conclusion

Phase 3 of the RFU Hub Preferences Security Implementation provides a comprehensive security framework for directory preference management. The implementation includes:

✅ **Core Security Components**: 8 fully implemented security modules
✅ **Database Foundation**: Complete schema with security features
✅ **User Interface**: Secure GUI with PII warnings and security controls
✅ **Comprehensive Testing**: Extensive test suite covering all components
✅ **Documentation**: Complete technical and security documentation

### Security Achievements
- **AES-256-GCM Encryption**: Enterprise-grade encryption for sensitive paths
- **Advanced PII Detection**: 20+ patterns with 5-level sensitivity scoring
- **Role-Based Access Control**: Hierarchical permission system
- **Comprehensive Audit Trail**: Full compliance and monitoring capabilities
- **Defense in Depth**: Multiple security layers for complete protection

### Next Steps
The Phase 3 implementation is complete and ready for integration with the broader RFU Hub system. Future enhancements may include:
- Additional PII detection patterns for specific industries
- Integration with external security systems
- Advanced analytics and reporting capabilities
- Mobile and web interface support

---

**Document Version**: 1.0.0  
**Last Updated**: January 2024  
**Classification**: Technical Documentation  
**Review Status**: Complete