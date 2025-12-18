# RFU Hub Security Framework - API Documentation

## Overview

The RFU Hub Security Framework provides comprehensive security capabilities for directory preference management, encryption, PII detection, audit logging, and access control. This documentation covers all public APIs across the security components implemented in Phases 1-3.

## Table of Contents

1. [Directory Security Manager](#directory-security-manager)
2. [Directory Encryption](#directory-encryption)
3. [PII Detection](#pii-detection)
4. [Directory Permissions](#directory-permissions)
5. [Directory Audit Logging](#directory-audit-logging)
6. [Database Manager](#database-manager)
7. [Migration Manager](#migration-manager)
8. [Configuration Manager](#configuration-manager)
9. [Error Handling](#error-handling)
10. [Performance Considerations](#performance-considerations)

---

## Directory Security Manager

The `DirectorySecurityManager` class provides the main interface for secure directory preference management.

### Class: `DirectorySecurityManager`

**Location:** `src/rfu/core/directory_security/directory_security_manager.py`

#### Constructor

```python
def __init__(self, database_manager: DatabaseManager, config_manager: Optional[ConfigManager] = None):
    """
    Initialize the Directory Security Manager.

    Args:
        database_manager (DatabaseManager): Database manager instance for data persistence
        config_manager (Optional[ConfigManager]): Configuration manager for security settings

    Raises:
        ValueError: If database_manager is None
        SecurityError: If security initialization fails
    """
```

#### Core Methods

##### `store_directory_preference`

```python
def store_directory_preference(self, user_id: str, tool_id: str, category: str,
                             directory_path: str) -> DirectorySecurityResult:
    """
    Securely store a directory preference with encryption and PII detection.

    Args:
        user_id (str): User identifier (must be non-empty)
        tool_id (str): Tool identifier (must be non-empty)
        category (str): Category for the preference
        directory_path (str): Directory path to store

    Returns:
        DirectorySecurityResult: Result object containing:
            - success (bool): Operation success status
            - path_hash (str): SHA-256 hash of the path for retrieval
            - pii_sensitive (bool): Whether PII was detected
            - encrypted (bool): Whether path was encrypted
            - error_message (str): Error details if operation failed

    Raises:
        ValueError: If required parameters are empty or None
        SecurityError: If encryption or storage fails

    Example:
        >>> result = security_manager.store_directory_preference(
        ...     "user123", "file_manager", "documents",
        ...     "C:\\Users\\john\\Documents\\Personal"
        ... )
        >>> if result.success:
        ...     print(f"Stored with hash: {result.path_hash}")
        ...     print(f"PII detected: {result.pii_sensitive}")
    """
```

##### `retrieve_directory_preference`

```python
def retrieve_directory_preference(self, user_id: str, path_hash: str) -> DirectorySecurityResult:
    """
    Retrieve and decrypt a stored directory preference.

    Args:
        user_id (str): User identifier
        path_hash (str): SHA-256 hash of the directory path

    Returns:
        DirectorySecurityResult: Result object containing:
            - success (bool): Operation success status
            - decrypted_path (str): Original directory path
            - pii_sensitive (bool): Whether PII was detected
            - encrypted (bool): Whether path was encrypted
            - metadata (dict): Additional metadata
            - error_message (str): Error details if operation failed

    Example:
        >>> result = security_manager.retrieve_directory_preference(
        ...     "user123", "abc123def456..."
        ... )
        >>> if result.success:
        ...     print(f"Original path: {result.decrypted_path}")
    """
```

##### `list_user_directories`

```python
def list_user_directories(self, user_id: Optional[str] = None) -> List[DirectoryInfo]:
    """
    List directory preferences for a user or all users.

    Args:
        user_id (Optional[str]): User ID to filter by. If None, returns all directories

    Returns:
        List[DirectoryInfo]: List of directory information objects containing:
            - path_hash (str): Hash identifier
            - user_id (str): User identifier
            - tool_id (str): Tool identifier
            - category (str): Directory category
            - pii_sensitive (bool): PII detection status
            - created_at (datetime): Creation timestamp
            - last_accessed (datetime): Last access timestamp

    Example:
        >>> directories = security_manager.list_user_directories("user123")
        >>> for dir_info in directories:
        ...     print(f"{dir_info.tool_id}: {dir_info.category}")
    """
```

##### `delete_directory_preference`

```python
def delete_directory_preference(self, user_id: str, path_hash: str) -> DirectorySecurityResult:
    """
    Securely delete a directory preference with audit logging.

    Args:
        user_id (str): User identifier
        path_hash (str): SHA-256 hash of the directory path

    Returns:
        DirectorySecurityResult: Result object with success status

    Example:
        >>> result = security_manager.delete_directory_preference(
        ...     "user123", "abc123def456..."
        ... )
        >>> print(f"Deleted: {result.success}")
    """
```

##### `update_directory_permissions`

```python
def update_directory_permissions(self, user_id: str, path_hash: str,
                               permissions: Dict[str, bool]) -> DirectorySecurityResult:
    """
    Update permissions for a directory preference.

    Args:
        user_id (str): User identifier
        path_hash (str): Directory path hash
        permissions (Dict[str, bool]): Permission settings
            - 'read': Read permission
            - 'write': Write permission
            - 'execute': Execute permission
            - 'share': Share permission

    Returns:
        DirectorySecurityResult: Result with updated permissions

    Example:
        >>> result = security_manager.update_directory_permissions(
        ...     "user123", "abc123def456...",
        ...     {"read": True, "write": False, "share": False}
        ... )
    """
```

---

## Directory Encryption

The `DirectoryPathEncryption` class provides secure encryption/decryption for directory paths.

### Class: `DirectoryPathEncryption`

**Location:** `src/rfu/core/directory_security/directory_encryption.py`

#### Constructor

```python
def __init__(self, config_manager: Optional[ConfigManager] = None):
    """
    Initialize directory path encryption with configurable parameters.

    Args:
        config_manager (Optional[ConfigManager]): Configuration for encryption settings
    """
```

#### Core Methods

##### `encrypt_directory_path`

```python
def encrypt_directory_path(self, directory_path: str, user_id: str) -> EncryptionResult:
    """
    Encrypt a directory path with user-specific key derivation.

    Args:
        directory_path (str): Directory path to encrypt
        user_id (str): User identifier for key derivation

    Returns:
        EncryptionResult: Result object containing:
            - success (bool): Encryption success status
            - encrypted_data (bytes): Encrypted path data
            - salt (bytes): Random salt used for key derivation
            - nonce (bytes): Random nonce for encryption
            - integrity_hash (str): HMAC for data integrity
            - error_message (str): Error details if encryption failed

    Security Features:
        - AES-256-GCM encryption
        - PBKDF2 key derivation with 100,000 iterations
        - Random salt generation (32 bytes)
        - Random nonce generation (12 bytes)
        - HMAC-SHA256 integrity protection
        - Timing attack resistance

    Performance:
        - Target: <100ms encryption time
        - Memory-efficient for large paths

    Example:
        >>> encryption = DirectoryPathEncryption()
        >>> result = encryption.encrypt_directory_path(
        ...     "C:\\Users\\john\\Documents\\Personal", "user123"
        ... )
        >>> if result.success:
        ...     print(f"Encrypted: {len(result.encrypted_data)} bytes")
    """
```

##### `decrypt_directory_path`

```python
def decrypt_directory_path(self, encrypted_data: bytes, salt: bytes,
                         nonce: bytes, user_id: str,
                         integrity_hash: str) -> DecryptionResult:
    """
    Decrypt a directory path with integrity verification.

    Args:
        encrypted_data (bytes): Encrypted path data
        salt (bytes): Salt used for key derivation
        nonce (bytes): Nonce used for encryption
        user_id (str): User identifier for key derivation
        integrity_hash (str): HMAC for integrity verification

    Returns:
        DecryptionResult: Result object containing:
            - success (bool): Decryption success status
            - decrypted_path (str): Original directory path
            - integrity_verified (bool): Integrity check result
            - error_message (str): Error details if decryption failed

    Security Features:
        - Integrity verification before decryption
        - Constant-time comparisons
        - Secure memory cleanup
        - Timing attack resistance

    Example:
        >>> result = encryption.decrypt_directory_path(
        ...     encrypted_data, salt, nonce, "user123", integrity_hash
        ... )
        >>> if result.success and result.integrity_verified:
        ...     print(f"Decrypted: {result.decrypted_path}")
    """
```

##### `generate_key_from_user`

```python
def generate_key_from_user(self, user_id: str, salt: bytes) -> bytes:
    """
    Generate encryption key from user ID and salt using PBKDF2.

    Args:
        user_id (str): User identifier
        salt (bytes): Random salt for key derivation

    Returns:
        bytes: 32-byte encryption key

    Security Features:
        - PBKDF2-HMAC-SHA256 with 100,000 iterations
        - 32-byte key length for AES-256
        - User isolation through unique key derivation

    Example:
        >>> salt = os.urandom(32)
        >>> key = encryption.generate_key_from_user("user123", salt)
        >>> print(f"Key length: {len(key)} bytes")
    """
```

---

## PII Detection

The `PIIDetector` class provides detection of Personally Identifiable Information in directory paths.

### Class: `PIIDetector`

**Location:** `src/rfu/core/directory_security/pii_detector.py`

#### Constructor

```python
def __init__(self, config_manager: Optional[ConfigManager] = None):
    """
    Initialize PII detector with configurable detection rules.

    Args:
        config_manager (Optional[ConfigManager]): Configuration for PII detection rules
    """
```

#### Core Methods

##### `detect_pii`

```python
def detect_pii(self, directory_path: str) -> PIIDetectionResult:
    """
    Detect PII in a directory path using multiple detection methods.

    Args:
        directory_path (str): Directory path to analyze

    Returns:
        PIIDetectionResult: Result object containing:
            - has_pii (bool): Whether PII was detected
            - pii_types (List[str]): Types of PII detected
            - confidence_score (float): Detection confidence (0.0-1.0)
            - detected_patterns (List[str]): Specific patterns found
            - recommendations (List[str]): Security recommendations

    Detection Categories:
        - Personal names in paths
        - Social Security Numbers (SSN)
        - Credit card numbers
        - Email addresses
        - Phone numbers
        - Date of birth patterns
        - Medical record indicators
        - Financial information keywords

    Example:
        >>> detector = PIIDetector()
        >>> result = detector.detect_pii("C:\\Users\\john.doe\\Documents\\SSN_123-45-6789.txt")
        >>> if result.has_pii:
        ...     print(f"PII types: {result.pii_types}")
        ...     print(f"Confidence: {result.confidence_score}")
    """
```

##### `analyze_path_components`

```python
def analyze_path_components(self, directory_path: str) -> List[ComponentAnalysis]:
    """
    Analyze individual path components for PII indicators.

    Args:
        directory_path (str): Directory path to analyze

    Returns:
        List[ComponentAnalysis]: Analysis results for each path component:
            - component (str): Path component text
            - pii_indicators (List[str]): PII indicators found
            - risk_level (str): Risk level (low/medium/high/critical)
            - suggestions (List[str]): Mitigation suggestions

    Example:
        >>> analyses = detector.analyze_path_components(
        ...     "C:\\Users\\john.doe\\Medical\\Records\\2024"
        ... )
        >>> for analysis in analyses:
        ...     if analysis.risk_level in ['high', 'critical']:
        ...         print(f"High risk: {analysis.component}")
    """
```

##### `get_pii_recommendations`

```python
def get_pii_recommendations(self, pii_types: List[str]) -> List[str]:
    """
    Get security recommendations based on detected PII types.

    Args:
        pii_types (List[str]): List of detected PII types

    Returns:
        List[str]: Security recommendations

    Example:
        >>> recommendations = detector.get_pii_recommendations(
        ...     ["ssn", "credit_card", "personal_name"]
        ... )
        >>> for rec in recommendations:
        ...     print(f"- {rec}")
    """
```

---

## Directory Permissions

The `DirectoryPermissionManager` class manages access permissions for directory preferences.

### Class: `DirectoryPermissionManager`

**Location:** `src/rfu/core/directory_security/directory_permissions.py`

#### Constructor

```python
def __init__(self, database_manager: DatabaseManager):
    """
    Initialize directory permission manager.

    Args:
        database_manager (DatabaseManager): Database manager for permission storage
    """
```

#### Core Methods

##### `set_permissions`

```python
def set_permissions(self, user_id: str, resource_id: str,
                   permissions: Dict[str, bool]) -> PermissionResult:
    """
    Set permissions for a directory resource.

    Args:
        user_id (str): User identifier
        resource_id (str): Directory resource identifier (path hash)
        permissions (Dict[str, bool]): Permission settings:
            - 'read': Read access permission
            - 'write': Write access permission
            - 'execute': Execute access permission
            - 'share': Share permission with other users
            - 'delete': Delete permission

    Returns:
        PermissionResult: Result object containing:
            - success (bool): Operation success status
            - permissions_set (Dict[str, bool]): Applied permissions
            - error_message (str): Error details if operation failed

    Example:
        >>> result = permission_manager.set_permissions(
        ...     "user123", "abc123def456...",
        ...     {"read": True, "write": True, "share": False}
        ... )
    """
```

##### `check_permission`

```python
def check_permission(self, user_id: str, resource_id: str,
                    permission_type: str) -> bool:
    """
    Check if user has specific permission for a resource.

    Args:
        user_id (str): User identifier
        resource_id (str): Directory resource identifier
        permission_type (str): Permission to check ('read', 'write', 'execute', 'share', 'delete')

    Returns:
        bool: True if user has permission, False otherwise

    Example:
        >>> has_write = permission_manager.check_permission(
        ...     "user123", "abc123def456...", "write"
        ... )
        >>> if has_write:
        ...     print("User can modify this directory preference")
    """
```

##### `get_user_permissions`

```python
def get_user_permissions(self, user_id: str, resource_id: str) -> Dict[str, bool]:
    """
    Get all permissions for a user on a specific resource.

    Args:
        user_id (str): User identifier
        resource_id (str): Directory resource identifier

    Returns:
        Dict[str, bool]: All permissions for the user on the resource

    Example:
        >>> permissions = permission_manager.get_user_permissions(
        ...     "user123", "abc123def456..."
        ... )
        >>> for perm, enabled in permissions.items():
        ...     print(f"{perm}: {enabled}")
    """
```

##### `revoke_permissions`

```python
def revoke_permissions(self, user_id: str, resource_id: str,
                      permission_types: List[str]) -> PermissionResult:
    """
    Revoke specific permissions for a user on a resource.

    Args:
        user_id (str): User identifier
        resource_id (str): Directory resource identifier
        permission_types (List[str]): Permissions to revoke

    Returns:
        PermissionResult: Result with revocation status

    Example:
        >>> result = permission_manager.revoke_permissions(
        ...     "user123", "abc123def456...", ["write", "delete"]
        ... )
    """
```

---

## Directory Audit Logging

The `DirectoryAuditLogger` class provides comprehensive audit logging for security events.

### Class: `DirectoryAuditLogger`

**Location:** `src/rfu/core/directory_security/directory_audit.py`

#### Constructor

```python
def __init__(self, database_manager: DatabaseManager, config_manager: Optional[ConfigManager] = None):
    """
    Initialize directory audit logger.

    Args:
        database_manager (DatabaseManager): Database manager for audit log storage
        config_manager (Optional[ConfigManager]): Configuration for audit settings
    """
```

#### Core Methods

##### `log_directory_operation`

```python
def log_directory_operation(self, user_id: str, resource_id: str,
                          operation_type: str, success: bool,
                          metadata: Optional[Dict] = None) -> bool:
    """
    Log a directory operation with comprehensive details.

    Args:
        user_id (str): User performing the operation
        resource_id (str): Directory resource identifier
        operation_type (str): Type of operation:
            - 'create': Directory preference creation
            - 'read': Directory preference retrieval
            - 'update': Directory preference modification
            - 'delete': Directory preference deletion
            - 'permission_change': Permission modification
            - 'share': Directory sharing operation
            - 'encrypt': Encryption operation
            - 'decrypt': Decryption operation
        success (bool): Whether operation succeeded
        metadata (Optional[Dict]): Additional operation metadata

    Returns:
        bool: True if audit log was successfully recorded

    Logged Information:
        - Timestamp (UTC with microsecond precision)
        - User identifier
        - Resource identifier
        - Operation type and result
        - IP address (if available)
        - User agent (if available)
        - Session identifier
        - Request metadata
        - Security context

    Example:
        >>> logged = audit_logger.log_directory_operation(
        ...     "user123", "abc123def456...", "create", True,
        ...     {"path_type": "personal", "pii_detected": True}
        ... )
    """
```

##### `log_security_event`

```python
def log_security_event(self, event_type: str, severity: str,
                      user_id: Optional[str], details: Dict) -> bool:
    """
    Log security-related events for monitoring and analysis.

    Args:
        event_type (str): Type of security event:
            - 'authentication_failure': Failed login attempts
            - 'encryption_failure': Encryption operation failures
            - 'permission_violation': Unauthorized access attempts
            - 'pii_exposure': Potential PII exposure
            - 'suspicious_activity': Unusual access patterns
            - 'data_breach_attempt': Potential data breach indicators
        severity (str): Event severity ('low', 'medium', 'high', 'critical')
        user_id (Optional[str]): User associated with event (if applicable)
        details (Dict): Event-specific details

    Returns:
        bool: True if security event was logged successfully

    Example:
        >>> logged = audit_logger.log_security_event(
        ...     "permission_violation", "high", "user123",
        ...     {"attempted_action": "delete", "resource": "abc123def456..."}
        ... )
    """
```

##### `get_audit_logs`

```python
def get_audit_logs(self, user_id: Optional[str] = None,
                  operation_type: Optional[str] = None,
                  start_date: Optional[datetime] = None,
                  end_date: Optional[datetime] = None,
                  limit: int = 100) -> List[AuditLogEntry]:
    """
    Retrieve audit logs with filtering options.

    Args:
        user_id (Optional[str]): Filter by user ID
        operation_type (Optional[str]): Filter by operation type
        start_date (Optional[datetime]): Filter by start date
        end_date (Optional[datetime]): Filter by end date
        limit (int): Maximum number of entries to return

    Returns:
        List[AuditLogEntry]: List of audit log entries containing:
            - timestamp (datetime): Operation timestamp
            - user_id (str): User identifier
            - resource_id (str): Resource identifier
            - operation_type (str): Operation type
            - success (bool): Operation result
            - metadata (Dict): Additional metadata
            - ip_address (str): User IP address
            - session_id (str): Session identifier

    Example:
        >>> logs = audit_logger.get_audit_logs(
        ...     user_id="user123",
        ...     operation_type="delete",
        ...     limit=50
        ... )
        >>> for log in logs:
        ...     print(f"{log.timestamp}: {log.operation_type} - {log.success}")
    """
```

##### `get_security_events`

```python
def get_security_events(self, severity: Optional[str] = None,
                       event_type: Optional[str] = None,
                       start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None,
                       limit: int = 100) -> List[SecurityEventEntry]:
    """
    Retrieve security events with filtering options.

    Args:
        severity (Optional[str]): Filter by severity level
        event_type (Optional[str]): Filter by event type
        start_date (Optional[datetime]): Filter by start date
        end_date (Optional[datetime]): Filter by end date
        limit (int): Maximum number of entries to return

    Returns:
        List[SecurityEventEntry]: List of security event entries

    Example:
        >>> events = audit_logger.get_security_events(
        ...     severity="high", limit=20
        ... )
        >>> for event in events:
        ...     print(f"ALERT: {event.event_type} - {event.details}")
    """
```

---

## Database Manager

The `DatabaseManager` class provides secure database operations with connection management.

### Class: `DatabaseManager`

**Location:** `src/rfu/database/database_manager.py`

#### Constructor

```python
def __init__(self, database_path: str, config_manager: Optional[ConfigManager] = None):
    """
    Initialize database manager with security configurations.

    Args:
        database_path (str): Path to SQLite database file
        config_manager (Optional[ConfigManager]): Configuration manager
    """
```

#### Core Methods

##### `execute_query`

```python
def execute_query(self, query: str, parameters: Optional[Tuple] = None) -> DatabaseResult:
    """
    Execute a SQL query with parameterized inputs for security.

    Args:
        query (str): SQL query with parameter placeholders
        parameters (Optional[Tuple]): Query parameters

    Returns:
        DatabaseResult: Query execution result

    Security Features:
        - Parameterized queries to prevent SQL injection
        - Connection pooling for performance
        - Transaction management
        - Error handling and logging

    Example:
        >>> result = db_manager.execute_query(
        ...     "SELECT * FROM directories WHERE user_id = ?", ("user123",)
        ... )
    """
```

##### `begin_transaction`

```python
def begin_transaction(self) -> bool:
    """Begin a database transaction for atomic operations."""
```

##### `commit_transaction`

```python
def commit_transaction(self) -> bool:
    """Commit the current database transaction."""
```

##### `rollback_transaction`

```python
def rollback_transaction(self) -> bool:
    """Rollback the current database transaction."""
```

---

## Migration Manager

The `MigrationManager` class handles database schema migrations and versioning.

### Class: `MigrationManager`

**Location:** `src/rfu/database/migration_manager.py`

#### Core Methods

##### `apply_pending_migrations`

```python
def apply_pending_migrations(self) -> bool:
    """
    Apply all pending database migrations.

    Returns:
        bool: True if all migrations applied successfully

    Performance Target: <30 seconds for all migrations

    Example:
        >>> migration_manager = MigrationManager(db_manager)
        >>> success = migration_manager.apply_pending_migrations()
        >>> if success:
        ...     print("All migrations applied successfully")
    """
```

##### `get_applied_migrations`

```python
def get_applied_migrations(self) -> List[str]:
    """
    Get list of applied migration versions.

    Returns:
        List[str]: List of applied migration identifiers
    """
```

---

## Configuration Manager

The `ConfigManager` class manages security configuration settings.

### Class: `ConfigManager`

**Location:** `src/config/config_manager.py`

#### Core Methods

##### `get_encryption_config`

```python
def get_encryption_config(self) -> Dict[str, Any]:
    """
    Get encryption configuration settings.

    Returns:
        Dict[str, Any]: Encryption configuration including:
            - algorithm: Encryption algorithm (AES-256-GCM)
            - key_iterations: PBKDF2 iterations (100,000)
            - salt_size: Salt size in bytes (32)
            - nonce_size: Nonce size in bytes (12)
    """
```

##### `get_pii_detection_config`

```python
def get_pii_detection_config(self) -> Dict[str, Any]:
    """
    Get PII detection configuration settings.

    Returns:
        Dict[str, Any]: PII detection configuration
    """
```

---

## Error Handling

### Exception Classes

#### `SecurityError`

```python
class SecurityError(Exception):
    """
    Raised when security operations fail.

    Attributes:
        message (str): Error description
        error_code (str): Specific error code
        context (Dict): Additional error context
    """
```

#### `EncryptionError`

```python
class EncryptionError(SecurityError):
    """Raised when encryption/decryption operations fail."""
```

#### `PermissionError`

```python
class PermissionError(SecurityError):
    """Raised when permission checks fail."""
```

### Result Classes

#### `DirectorySecurityResult`

```python
class DirectorySecurityResult:
    """
    Result object for directory security operations.

    Attributes:
        success (bool): Operation success status
        path_hash (str): SHA-256 hash of directory path
        pii_sensitive (bool): PII detection result
        encrypted (bool): Encryption status
        decrypted_path (str): Decrypted path (for retrieval)
        metadata (Dict): Additional operation metadata
        error_message (str): Error details if operation failed
    """
```

---

## Performance Considerations

### Encryption Performance

- **Target Latency:** <100ms for encryption/decryption operations
- **Memory Usage:** Efficient handling of large directory paths
- **Concurrent Operations:** Thread-safe with connection pooling

### Database Performance

- **Size Growth:** <5% database size increase with security enhancements
- **Query Performance:** Optimized indexes for common access patterns
- **Connection Management:** Connection pooling for scalability

### Security Performance

- **Key Derivation:** PBKDF2 with 100,000 iterations for timing attack resistance
- **Integrity Checks:** HMAC verification with constant-time comparisons
- **Audit Logging:** Asynchronous logging to minimize performance impact

---

## Security Best Practices

### API Usage Guidelines

1. **Always validate input parameters** before passing to API methods
2. **Handle errors appropriately** and log security events
3. **Use transaction management** for atomic operations
4. **Implement proper session management** for user context
5. **Regular audit log review** for security monitoring

### Performance Optimization

1. **Batch operations** when possible to reduce database overhead
2. **Use connection pooling** for high-concurrency scenarios
3. **Implement caching** for frequently accessed directory preferences
4. **Monitor performance metrics** and optimize based on usage patterns

### Security Monitoring

1. **Monitor failed operations** for potential security threats
2. **Set up alerts** for high-severity security events
3. **Regular security audits** of permissions and access patterns
4. **Backup and disaster recovery** planning for security data

---

## Version Information

- **API Version:** 1.0.0
- **Security Framework Version:** Phase 1-3 Complete
- **Database Schema Version:** Latest migration applied
- **Compatibility:** Python 3.8+, SQLite 3.35+

---

## Support and Contact

For API support, security questions, or bug reports, please refer to the project documentation or contact the development team.

**Last Updated:** 2024  
**Documentation Version:** 1.0.0
