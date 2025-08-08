# Phase 3: Directory Preferences Security Controls and PII Protection - Complete Specification

## Directory Path Encryption (Continued)

```python
    def decrypt_directory_path(self, encrypted_data: bytes, salt: bytes, 
                              nonce: bytes, integrity_hash: str, user_id: str) -> DirectoryDecryptionResult:
        """
        Decrypt directory path with integrity verification
        
        Args:
            encrypted_data: Encrypted directory path data
            salt: Salt used for key derivation
            nonce: Nonce used for encryption
            integrity_hash: Expected integrity hash
            user_id: User identifier for key derivation
            
        Returns:
            DirectoryDecryptionResult with decrypted path or error
        """
        try:
            # Verify integrity first
            calculated_hash = self._create_integrity_hash(encrypted_data, salt, nonce)
            if not self._verify_integrity_hash(calculated_hash, integrity_hash):
                return DirectoryDecryptionResult(
                    success=False,
                    error="Integrity verification failed - data may be corrupted"
                )
            
            # Derive key
            key = self._derive_directory_key(user_id, salt)
            
            # Decrypt data
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            aesgcm = AESGCM(key)
            decrypted_data = aesgcm.decrypt(nonce, encrypted_data, None)
            
            # Convert back to string
            directory_path = decrypted_data.decode('utf-8')
            
            return DirectoryDecryptionResult(
                success=True,
                directory_path=directory_path
            )
            
        except Exception as e:
            self.logger.error(f"Directory path decryption failed: {e}")
            return DirectoryDecryptionResult(
                success=False,
                error=f"Decryption failed: {e}"
            )
    
    def _derive_directory_key(self, user_id: str, salt: bytes) -> bytes:
        """Derive directory-specific encryption key"""
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        
        master_key = self.key_manager.get_directory_master_key()
        user_salt = salt + f"directory_{user_id}".encode('utf-8')
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=user_salt,
            iterations=self.key_iterations,
        )
        return kdf.derive(master_key)
    
    def _create_secure_path_hash(self, directory_path: str, user_id: str) -> str:
        """Create secure hash for path indexing without revealing path"""
        import hmac
        import hashlib
        
        # Use HMAC with user-specific key for secure hashing
        key = f"path_hash_{user_id}".encode('utf-8')
        path_bytes = directory_path.encode('utf-8')
        
        hash_obj = hmac.new(key, path_bytes, hashlib.sha256)
        return base64.b64encode(hash_obj.digest()).decode('utf-8')
    
    def _create_integrity_hash(self, encrypted_data: bytes, salt: bytes, nonce: bytes) -> str:
        """Create integrity hash for encrypted data"""
        from cryptography.hazmat.primitives import hashes
        
        digest = hashes.Hash(hashes.SHA256())
        digest.update(encrypted_data)
        digest.update(salt)
        digest.update(nonce)
        return base64.b64encode(digest.finalize()).decode('utf-8')

@dataclass
class DirectoryEncryptionResult:
    success: bool
    encrypted_data: Optional[bytes] = None
    salt: Optional[bytes] = None
    nonce: Optional[bytes] = None
    path_hash: Optional[str] = None
    integrity_hash: Optional[str] = None
    encryption_version: Optional[int] = None
    error: Optional[str] = None

@dataclass
class DirectoryDecryptionResult:
    success: bool
    directory_path: Optional[str] = None
    error: Optional[str] = None
```

### 5. Permission Management System

#### 5.1 DirectoryPermissionManager

**File:** `src/rfu/core/directory_security/permission_manager.py`

```python
class DirectoryPermissionManager:
    """
    Manages directory access permissions with role-based access control,
    temporary permissions, and comprehensive audit logging.
    """
    
    def __init__(self, database_manager: DatabaseManager):
        self.db_manager = database_manager
        self.permission_cache = DirectoryPermissionCache()
        self.logger = logging.getLogger('RFU.DirectoryPermissionManager')
    
    def check_directory_permission(self, user_id: str, directory_identifier: str, 
                                  operation: str) -> PermissionCheckResult:
        """
        Check if user has permission for directory operation
        
        Args:
            user_id: User identifier
            directory_identifier: Directory path or hash
            operation: Operation type ('read', 'write', 'delete', 'admin')
            
        Returns:
            PermissionCheckResult with authorization decision
        """
        try:
            # Check cache first
            cached_result = self.permission_cache.get_permission(
                user_id, directory_identifier, operation
            )
            if cached_result:
                return cached_result
            
            # Check user's base permissions
            base_permissions = self._get_user_base_permissions(user_id)
            
            # Check directory-specific permissions
            directory_permissions = self._get_directory_permissions(
                user_id, directory_identifier
            )
            
            # Check temporary permissions
            temp_permissions = self._get_temporary_permissions(
                user_id, directory_identifier
            )
            
            # Evaluate permission hierarchy
            permission_result = self._evaluate_permissions(
                operation, base_permissions, directory_permissions, temp_permissions
            )
            
            # Cache result
            self.permission_cache.cache_permission(
                user_id, directory_identifier, operation, permission_result
            )
            
            return permission_result
            
        except Exception as e:
            self.logger.error(f"Permission check failed: {e}")
            return PermissionCheckResult(
                authorized=False,
                reason=f"Permission system error: {e}"
            )
    
    def grant_directory_permission(self, granter_user_id: str, target_user_id: str,
                                  directory_identifier: str, permission_type: str,
                                  expires_at: Optional[datetime] = None) -> PermissionGrantResult:
        """
        Grant directory permission to user
        
        Args:
            granter_user_id: User granting the permission
            target_user_id: User receiving the permission
            directory_identifier: Directory path or hash
            permission_type: Permission type to grant
            expires_at: Optional expiration time
            
        Returns:
            PermissionGrantResult with grant outcome
        """
        try:
            # Check if granter has admin permission
            granter_check = self.check_directory_permission(
                granter_user_id, directory_identifier, 'admin'
            )
            
            if not granter_check.authorized:
                return PermissionGrantResult(
                    success=False,
                    error="Granter lacks admin permission for this directory"
                )
            
            # Validate permission type
            if permission_type not in ['read', 'write', 'delete', 'admin']:
                return PermissionGrantResult(
                    success=False,
                    error=f"Invalid permission type: {permission_type}"
                )
            
            # Insert permission record
            permission_id = self._insert_permission_record(
                target_user_id, directory_identifier, permission_type,
                granter_user_id, expires_at
            )
            
            # Invalidate cache
            self.permission_cache.invalidate_user_permissions(target_user_id)
            
            # Log permission grant
            self._log_permission_change(
                'grant', granter_user_id, target_user_id, 
                directory_identifier, permission_type
            )
            
            return PermissionGrantResult(
                success=True,
                permission_id=permission_id
            )
            
        except Exception as e:
            self.logger.error(f"Permission grant failed: {e}")
            return PermissionGrantResult(
                success=False,
                error=f"Grant system error: {e}"
            )
    
    def revoke_directory_permission(self, revoker_user_id: str, target_user_id: str,
                                   directory_identifier: str, permission_type: str) -> PermissionRevokeResult:
        """Revoke directory permission from user"""
        try:
            # Check if revoker has admin permission
            revoker_check = self.check_directory_permission(
                revoker_user_id, directory_identifier, 'admin'
            )
            
            if not revoker_check.authorized:
                return PermissionRevokeResult(
                    success=False,
                    error="Revoker lacks admin permission for this directory"
                )
            
            # Revoke permission
            affected_rows = self.db_manager.execute_update("""
                UPDATE directory_permissions 
                SET is_active = FALSE, revoked_at = CURRENT_TIMESTAMP, revoked_by = ?
                WHERE user_id = ? AND directory_hash = ? AND permission_type = ? AND is_active = TRUE
            """, (revoker_user_id, target_user_id, directory_identifier, permission_type))
            
            if affected_rows == 0:
                return PermissionRevokeResult(
                    success=False,
                    error="Permission not found or already revoked"
                )
            
            # Invalidate cache
            self.permission_cache.invalidate_user_permissions(target_user_id)
            
            # Log permission revocation
            self._log_permission_change(
                'revoke', revoker_user_id, target_user_id,
                directory_identifier, permission_type
            )
            
            return PermissionRevokeResult(success=True)
            
        except Exception as e:
            self.logger.error(f"Permission revoke failed: {e}")
            return PermissionRevokeResult(
                success=False,
                error=f"Revoke system error: {e}"
            )
    
    def _get_user_base_permissions(self, user_id: str) -> List[str]:
        """Get user's base permission level"""
        
        permissions = self.db_manager.execute_query("""
            SELECT permission_type FROM user_base_permissions 
            WHERE user_id = ? AND is_active = TRUE
        """, (user_id,))
        
        return [perm['permission_type'] for perm in permissions]
    
    def _get_directory_permissions(self, user_id: str, directory_identifier: str) -> List[Dict[str, Any]]:
        """Get directory-specific permissions"""
        
        permissions = self.db_manager.execute_query("""
            SELECT permission_type, expires_at, granted_at 
            FROM directory_permissions 
            WHERE user_id = ? AND directory_hash = ? AND is_active = TRUE
        """, (user_id, directory_identifier))
        
        # Filter out expired permissions
        active_permissions = []
        current_time = datetime.now()
        
        for perm in permissions:
            if perm['expires_at']:
                expires_at = datetime.fromisoformat(perm['expires_at'])
                if current_time > expires_at:
                    # Mark as expired
                    self._expire_permission(user_id, directory_identifier, perm['permission_type'])
                    continue
            
            active_permissions.append(perm)
        
        return active_permissions
    
    def _evaluate_permissions(self, operation: str, base_permissions: List[str],
                            directory_permissions: List[Dict[str, Any]],
                            temp_permissions: List[Dict[str, Any]]) -> PermissionCheckResult:
        """Evaluate permission hierarchy to determine authorization"""
        
        # Permission hierarchy: admin > delete > write > read
        permission_hierarchy = {
            'read': 1,
            'write': 2,
            'delete': 3,
            'admin': 4
        }
        
        required_level = permission_hierarchy.get(operation, 0)
        if required_level == 0:
            return PermissionCheckResult(
                authorized=False,
                reason=f"Unknown operation: {operation}"
            )
        
        # Check base permissions
        max_base_level = 0
        for perm in base_permissions:
            level = permission_hierarchy.get(perm, 0)
            max_base_level = max(max_base_level, level)
        
        # Check directory permissions
        max_directory_level = 0
        for perm in directory_permissions:
            level = permission_hierarchy.get(perm['permission_type'], 0)
            max_directory_level = max(max_directory_level, level)
        
        # Check temporary permissions
        max_temp_level = 0
        for perm in temp_permissions:
            level = permission_hierarchy.get(perm['permission_type'], 0)
            max_temp_level = max(max_temp_level, level)
        
        # Use highest permission level
        max_level = max(max_base_level, max_directory_level, max_temp_level)
        
        if max_level >= required_level:
            return PermissionCheckResult(
                authorized=True,
                permission_source=self._determine_permission_source(
                    max_level, max_base_level, max_directory_level, max_temp_level
                )
            )
        else:
            return PermissionCheckResult(
                authorized=False,
                reason=f"Insufficient permission level: {max_level} < {required_level}"
            )

@dataclass
class PermissionCheckResult:
    authorized: bool
    reason: Optional[str] = None
    permission_source: Optional[str] = None
    permissions: List[str] = field(default_factory=list)

@dataclass
class PermissionGrantResult:
    success: bool
    permission_id: Optional[str] = None
    error: Optional[str] = None

@dataclass
class PermissionRevokeResult:
    success: bool
    error: Optional[str] = None
```

### 6. Audit Logging System

#### 6.1 DirectoryAuditLogger

**File:** `src/rfu/core/directory_security/directory_audit.py`

```python
class DirectoryAuditLogger:
    """
    Comprehensive audit logging for directory operations with
    anonymization, integrity protection, and compliance features.
    """
    
    def __init__(self, database_manager: DatabaseManager):
        self.db_manager = database_manager
        self.anonymizer = DirectoryPathAnonymizer()
        self.logger = logging.getLogger('RFU.DirectoryAuditLogger')
    
    def log_directory_operation(self, user_id: str, directory_hash: str, 
                               operation: str, success: bool, 
                               metadata: Dict[str, Any] = None) -> None:
        """
        Log directory operation with comprehensive audit information
        
        Args:
            user_id: User performing the operation
            directory_hash: Anonymized directory identifier
            operation: Operation type
            success: Whether operation succeeded
            metadata: Additional operation metadata
        """
        try:
            # Get session information
            session_info = self._get_session_info()
            
            # Create audit record
            audit_record = {
                'user_id': user_id,
                'directory_hash': directory_hash,
                'operation': operation,
                'success': success,
                'timestamp': datetime.now().isoformat(),
                'session_id': session_info.get('session_id'),
                'ip_address': session_info.get('ip_address'),
                'user_agent': session_info.get('user_agent'),
                'metadata': json.dumps(metadata) if metadata else None,
                'audit_version': '1.0'
            }
            
            # Insert audit record
            self.db_manager.execute_update("""
                INSERT INTO directory_access_audit 
                (user_id, directory_hash, operation, success, timestamp, 
                 session_id, ip_address, user_agent, metadata, audit_version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                audit_record['user_id'],
                audit_record['directory_hash'],
                audit_record['operation'],
                audit_record['success'],
                audit_record['timestamp'],
                audit_record['session_id'],
                audit_record['ip_address'],
                audit_record['user_agent'],
                audit_record['metadata'],
                audit_record['audit_version']
            ))
            
            # Log to file for backup
            self._log_to_file(audit_record)
            
        except Exception as e:
            self.logger.error(f"Audit logging failed: {e}")
            # Don't raise exception to avoid breaking main operation
    
    def log_access_denied(self, user_id: str, directory_identifier: str, 
                         operation: str, reason: str) -> None:
        """Log access denied events for security monitoring"""
        
        self.log_directory_operation(
            user_id, directory_identifier, f"{operation}_denied", False, {
                'denial_reason': reason,
                'security_event': True,
                'severity': 'medium'
            }
        )
    
    def log_security_violation(self, user_id: str, directory_path: str, 
                              violation_type: str, details: Dict[str, Any]) -> None:
        """Log security violations for immediate attention"""
        
        # Anonymize path for logging
        anonymized_path = self.anonymizer.anonymize_path(directory_path)
        
        self.log_directory_operation(
            user_id, anonymized_path, 'security_violation', False, {
                'violation_type': violation_type,
                'violation_details': details,
                'security_event': True,
                'severity': 'high',
                'requires_investigation': True
            }
        )
        
        # Also log to security event system
        self._log_security_event(user_id, violation_type, details)
    
    def generate_audit_report(self, start_date: datetime, end_date: datetime,
                             user_id: Optional[str] = None) -> AuditReport:
        """Generate comprehensive audit report for specified period"""
        
        try:
            # Build query conditions
            conditions = ["timestamp BETWEEN ? AND ?"]
            params = [start_date.isoformat(), end_date.isoformat()]
            
            if user_id:
                conditions.append("user_id = ?")
                params.append(user_id)
            
            # Get audit records
            query = f"""
                SELECT user_id, directory_hash, operation, success, timestamp,
                       ip_address, metadata
                FROM directory_access_audit 
                WHERE {' AND '.join(conditions)}
                ORDER BY timestamp DESC
            """
            
            records = self.db_manager.execute_query(query, params)
            
            # Analyze records
            analysis = self._analyze_audit_records(records)
            
            return AuditReport(
                start_date=start_date,
                end_date=end_date,
                total_operations=len(records),
                successful_operations=analysis['successful_count'],
                failed_operations=analysis['failed_count'],
                security_violations=analysis['security_violations'],
                unique_users=analysis['unique_users'],
                operation_breakdown=analysis['operation_breakdown'],
                records=records
            )
            
        except Exception as e:
            self.logger.error(f"Audit report generation failed: {e}")
            return AuditReport(
                start_date=start_date,
                end_date=end_date,
                error=f"Report generation failed: {e}"
            )
    
    def _analyze_audit_records(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze audit records for report generation"""
        
        analysis = {
            'successful_count': 0,
            'failed_count': 0,
            'security_violations': 0,
            'unique_users': set(),
            'operation_breakdown': {}
        }
        
        for record in records:
            # Count success/failure
            if record['success']:
                analysis['successful_count'] += 1
            else:
                analysis['failed_count'] += 1
            
            # Track unique users
            analysis['unique_users'].add(record['user_id'])
            
            # Count operations
            operation = record['operation']
            analysis['operation_breakdown'][operation] = \
                analysis['operation_breakdown'].get(operation, 0) + 1
            
            # Check for security violations
            if record['metadata']:
                try:
                    metadata = json.loads(record['metadata'])
                    if metadata.get('security_event'):
                        analysis['security_violations'] += 1
                except json.JSONDecodeError:
                    pass
        
        # Convert set to count
        analysis['unique_users'] = len(analysis['unique_users'])
        
        return analysis

@dataclass
class AuditReport:
    start_date: datetime
    end_date: datetime
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    security_violations: int = 0
    unique_users: int = 0
    operation_breakdown: Dict[str, int] = field(default_factory=dict)
    records: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None
```

### 7. Database Schema for Directory Security

```sql
-- Secure directory storage with encryption
CREATE TABLE IF NOT EXISTS secure_directories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL DEFAULT 'default',
    tool_name TEXT NOT NULL,
    directory_type TEXT NOT NULL CHECK (directory_type IN ('favorite', 'recent', 'default', 'custom')),
    encrypted_path BLOB NOT NULL,
    salt BLOB NOT NULL,
    nonce BLOB NOT NULL,
    path_hash TEXT NOT NULL UNIQUE, -- For duplicate detection without exposing path
    integrity_hash TEXT NOT NULL,
    encryption_version INTEGER DEFAULT 1,
    permission_level INTEGER NOT NULL DEFAULT 1, -- 1=read, 2=write, 3=admin
    is_pii_sensitive BOOLEAN DEFAULT FALSE,
    sensitivity_level INTEGER DEFAULT 1, -- 1-5 scale
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP,
    last_validated TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP, -- Optional expiration for temporary directories
    UNIQUE(user_id, tool_name, directory_type, path_hash)
);

-- Directory access permissions
CREATE TABLE IF NOT EXISTS directory_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    directory_hash TEXT NOT NULL,
    permission_type TEXT NOT NULL CHECK (permission_type IN ('read', 'write', 'delete', 'admin')),
    granted_by TEXT NOT NULL,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    revoked_at TIMESTAMP,
    revoked_by TEXT,
    conditions TEXT, -- JSON conditions for conditional access
    permission_scope TEXT DEFAULT 'full', -- 'full', 'limited', 'temporary'
    UNIQUE(user_id, directory_hash, permission_type)
);

-- User base permissions
CREATE TABLE IF NOT EXISTS user_base_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    permission_type TEXT NOT NULL CHECK (permission_type IN ('read', 'write', 'delete', 'admin')),
    granted_by TEXT NOT NULL,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    scope TEXT DEFAULT 'global', -- 'global', 'tool_specific', 'directory_specific'
    UNIQUE(user_id, permission_type, scope)
);

-- Directory access audit log with anonymization
CREATE TABLE IF NOT EXISTS directory_access_audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    directory_hash TEXT NOT NULL, -- Anonymized directory reference
    operation TEXT NOT NULL CHECK (operation IN (
        'store', 'retrieve', 'delete', 'validate', 'encrypt', 'decrypt',
        'read_denied', 'write_denied', 'delete_denied', 'security_violation'
    )),
    success BOOLEAN NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_id TEXT,
    ip_address TEXT,
    user_agent TEXT,
    metadata TEXT, -- JSON metadata about the operation
    audit_version TEXT DEFAULT '1.0',
    severity TEXT DEFAULT 'normal' CHECK (severity IN ('low', 'normal', 'medium', 'high', 'critical'))
);

-- PII detection and classification log
CREATE TABLE IF NOT EXISTS pii_detection_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    directory_hash TEXT NOT NULL,
    pii_indicators TEXT NOT NULL, -- JSON array of detected PII types
    sensitivity_level INTEGER NOT NULL,
    detection_confidence REAL NOT NULL, -- 0.0 to 1.0
    anonymized_path TEXT NOT NULL,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    detection_version TEXT DEFAULT '1.0',
    requires_encryption BOOLEAN DEFAULT FALSE
);

-- Directory encryption keys management
CREATE TABLE IF NOT EXISTS directory_encryption_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_id TEXT NOT NULL UNIQUE,
    key_type TEXT NOT NULL CHECK (key_type IN ('master', 'user', 'directory', 'backup')),
    encrypted_key BLOB NOT NULL,
    salt BLOB NOT NULL,
    key_version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    rotation_count INTEGER DEFAULT 0,
    last_used TIMESTAMP,
    usage_count INTEGER DEFAULT 0
);

-- Security violations and incidents
CREATE TABLE IF NOT EXISTS directory_security_incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id TEXT NOT NULL UNIQUE,
    user_id TEXT NOT NULL,
    incident_type TEXT NOT NULL CHECK (incident_type IN (
        'path_traversal', 'unauthorized_access', 'permission_escalation',
        'pii_exposure', 'encryption_failure', 'integrity_violation'
    )),
    severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    description TEXT NOT NULL,
    affected_directory_hash TEXT,
    detection_method TEXT NOT NULL,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    resolution_notes TEXT,
    status TEXT DEFAULT 'open' CHECK (status IN ('open', 'investigating', 'resolved', 'false_positive')),
    metadata TEXT -- JSON additional incident data
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_secure_directories_user_tool ON secure_directories(user_id, tool_name);
CREATE INDEX IF NOT EXISTS idx_secure_directories_hash ON secure_directories(path_hash);
CREATE INDEX IF NOT EXISTS idx_secure_directories_pii ON secure_directories(is_pii_sensitive, sensitivity_level);
CREATE INDEX IF NOT EXISTS idx_directory_permissions_user ON directory_permissions(user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_directory_permissions_hash ON directory_permissions(directory_hash, is_active);
CREATE INDEX IF NOT EXISTS idx_directory_audit_user_time ON directory_access_audit(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_directory_audit_operation ON directory_access_audit(operation, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_directory_audit_severity ON directory_access_audit(severity, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_pii_detection_sensitivity ON pii_detection_log(sensitivity_level, detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_security_incidents_status ON directory_security_incidents(status, severity, detected_at DESC);
```

### 8. Integration with Preferences Menu

#### 8.1 Secure Directory Preferences Widget

**File:** `src/rfu/gui/secure_directory_preferences.py`

```python
class SecureDirectoryPreferencesWidget(QWidget):
    """
    Enhanced directory preferences widget with security features,
    PII protection, and comprehensive audit logging.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.directory_security_manager = DirectorySecurityManager(get_database_manager())
        self.permission_manager = DirectoryPermissionManager(get_database_manager())
        self.setup_ui()
        self.setup_security_monitoring()
    
    def setup_ui(self):
        """Setup secure directory preferences UI"""
        layout = QVBoxLayout(self)
        
        # Security status indicator
        self.security_status = DirectorySecurityStatusWidget()
        layout.addWidget(self.security_status)
        
        # Tool-specific directory management
        self.tool_tabs = QTabWidget()
        self.setup_tool_tabs()
        layout.addWidget(self.tool_tabs)
        
        # Security controls
        self.security_controls = DirectorySecurityControlsWidget()
        layout.addWidget(self.security_controls)
        
        # Audit log viewer
        self.audit_viewer = DirectoryAuditViewer()
        layout.addWidget(self.audit_viewer)
    
    def add_directory_preference(self, tool_name: str, directory_type: str, directory_path: str):
        """Add directory preference with security validation"""
        
        try:
            # Show security warning for PII-sensitive paths
            pii_result = self.directory_security_manager.pii_detector.analyze_directory_path(directory_path)
            
            if pii_result.contains_pii:
                warning_result = self.show_pii_warning_dialog(pii_result)
                if warning_result != QDialog.Accepted:
                    return
            
            # Store directory securely
            storage_result = self.directory_security_manager.store_directory_preference(
                self.get_current_user_id(), tool_name, directory_type, directory_path
            )
            
            if storage_result.success:
                self.refresh_directory_list(tool_name)
                self.security_status.update_status(
                    "success", 
                    f"Directory added successfully (PII: {'Yes' if storage_result.pii_sensitive else 'No'})"
                )
            else:
                if storage_result.security_violation:
                    self.show_security_violation_dialog(storage_result.error)
                else:
                    QMessageBox.warning(self, "Error", storage_result.error)
                    
        except Exception as e:
            self.logger.error(f"Directory addition failed: {e}")
            QMessageBox.critical(self, "Error", f"Failed to add directory: {e}")
    
    def show_pii_warning_dialog(self, pii_result: PIIAnalysisResult) -> int:
        """Show PII warning dialog to user"""
        
        dialog = PIIWarningDialog(pii_result, self)
        return dialog.exec_()
    
    def show_security_violation_dialog(self, error_message: str):
        """Show security violation dialog"""
        
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Warning)
        dialog.setWindowTitle("Security Violation Detected")
        dialog.setText("A security violation was detected while processing your request.")
        dialog.setDetailedText