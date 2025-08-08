# Phase 2: Theme Data Privacy Protection and Corruption Handling

## Technical Specification

### Overview

This specification details the implementation of comprehensive privacy protection and corruption-handling safeguards for persisted theme data storage in the RFU Hub project. The system provides data validation, integrity checks, error recovery mechanisms, and secure storage practices to prevent unauthorized access or data loss.

## Architecture Components

### 1. Theme Security Framework

#### 1.1 ThemeSecurityManager

**File:** `src/rfu/core/theme_security/theme_security_manager.py`

```python
class ThemeSecurityManager:
    """
    Central manager for theme security operations including encryption,
    validation, access control, and audit logging.
    """
    
    def __init__(self, database_manager: DatabaseManager):
        self.db_manager = database_manager
        self.encryption = ThemeDataEncryption()
        self.validator = ThemeIntegrityValidator()
        self.access_control = ThemeAccessController(database_manager)
        self.backup_manager = ThemeBackupManager(database_manager)
        self.audit_logger = ThemeAuditLogger(database_manager)
        self.logger = logging.getLogger('RFU.ThemeSecurityManager')
    
    def store_theme_securely(self, user_id: str, theme_name: str, theme_data: Dict[str, Any]) -> SecureStorageResult:
        """Store theme data with encryption and integrity protection"""
        
    def retrieve_theme_securely(self, user_id: str, theme_name: str) -> SecureRetrievalResult:
        """Retrieve and decrypt theme data with integrity verification"""
        
    def validate_theme_integrity(self, user_id: str, theme_name: str) -> IntegrityValidationResult:
        """Validate theme data integrity and detect corruption"""
        
    def recover_corrupted_theme(self, user_id: str, theme_name: str) -> RecoveryResult:
        """Recover corrupted theme from backup or defaults"""
        
    def audit_theme_access(self, user_id: str, theme_name: str, operation: str, success: bool, metadata: Dict[str, Any] = None) -> None:
        """Log theme access for security auditing"""
```

### 2. Encryption and Data Protection

#### 2.1 ThemeDataEncryption

**File:** `src/rfu/core/theme_security/theme_encryption.py`

```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import base64
import json

class ThemeDataEncryption:
    """
    Handles AES-256-GCM encryption for theme data with key derivation
    and integrity protection using authenticated encryption.
    """
    
    def __init__(self):
        self.key_manager = SecureKeyManager()
        self.salt_length = 32
        self.nonce_length = 12
        self.key_iterations = 100000
        
    def encrypt_theme_data(self, theme_data: Dict[str, Any], user_id: str) -> EncryptionResult:
        """
        Encrypt theme data using AES-256-GCM with user-specific key derivation
        
        Args:
            theme_data: Theme configuration dictionary
            user_id: User identifier for key derivation
            
        Returns:
            EncryptionResult containing encrypted data, salt, nonce, and metadata
        """
        try:
            # Serialize theme data
            serialized_data = json.dumps(theme_data, sort_keys=True).encode('utf-8')
            
            # Generate salt and derive key
            salt = os.urandom(self.salt_length)
            key = self._derive_key(user_id, salt)
            
            # Generate nonce for AEAD
            nonce = os.urandom(self.nonce_length)
            
            # Encrypt with AEAD
            aesgcm = AESGCM(key)
            encrypted_data = aesgcm.encrypt(nonce, serialized_data, None)
            
            # Create integrity hash
            integrity_hash = self._create_integrity_hash(encrypted_data, salt, nonce)
            
            return EncryptionResult(
                success=True,
                encrypted_data=encrypted_data,
                salt=salt,
                nonce=nonce,
                integrity_hash=integrity_hash,
                encryption_version=1
            )
            
        except Exception as e:
            self.logger.error(f"Theme encryption failed for user {user_id}: {e}")
            return EncryptionResult(success=False, error=str(e))
    
    def decrypt_theme_data(self, encrypted_data: bytes, salt: bytes, nonce: bytes, 
                          integrity_hash: str, user_id: str) -> DecryptionResult:
        """
        Decrypt theme data with integrity verification
        
        Args:
            encrypted_data: Encrypted theme data
            salt: Salt used for key derivation
            nonce: Nonce used for encryption
            integrity_hash: Expected integrity hash
            user_id: User identifier for key derivation
            
        Returns:
            DecryptionResult containing decrypted theme data or error
        """
        try:
            # Verify integrity first
            calculated_hash = self._create_integrity_hash(encrypted_data, salt, nonce)
            if not self._verify_integrity_hash(calculated_hash, integrity_hash):
                return DecryptionResult(
                    success=False, 
                    error="Integrity verification failed - data may be corrupted"
                )
            
            # Derive key
            key = self._derive_key(user_id, salt)
            
            # Decrypt data
            aesgcm = AESGCM(key)
            decrypted_data = aesgcm.decrypt(nonce, encrypted_data, None)
            
            # Deserialize theme data
            theme_data = json.loads(decrypted_data.decode('utf-8'))
            
            return DecryptionResult(
                success=True,
                theme_data=theme_data
            )
            
        except Exception as e:
            self.logger.error(f"Theme decryption failed for user {user_id}: {e}")
            return DecryptionResult(success=False, error=str(e))
    
    def _derive_key(self, user_id: str, salt: bytes) -> bytes:
        """Derive encryption key using PBKDF2"""
        master_key = self.key_manager.get_master_key()
        user_salt = salt + user_id.encode('utf-8')
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=user_salt,
            iterations=self.key_iterations,
        )
        return kdf.derive(master_key)
    
    def _create_integrity_hash(self, encrypted_data: bytes, salt: bytes, nonce: bytes) -> str:
        """Create SHA-256 integrity hash"""
        digest = hashes.Hash(hashes.SHA256())
        digest.update(encrypted_data)
        digest.update(salt)
        digest.update(nonce)
        return base64.b64encode(digest.finalize()).decode('utf-8')
    
    def _verify_integrity_hash(self, calculated: str, expected: str) -> bool:
        """Verify integrity hash using constant-time comparison"""
        return hmac.compare_digest(calculated, expected)

@dataclass
class EncryptionResult:
    success: bool
    encrypted_data: Optional[bytes] = None
    salt: Optional[bytes] = None
    nonce: Optional[bytes] = None
    integrity_hash: Optional[str] = None
    encryption_version: Optional[int] = None
    error: Optional[str] = None

@dataclass
class DecryptionResult:
    success: bool
    theme_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
```

#### 2.2 SecureKeyManager

**File:** `src/rfu/core/theme_security/secure_key_manager.py`

```python
import keyring
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

class SecureKeyManager:
    """
    Manages encryption keys using OS keyring with secure key derivation
    and rotation capabilities.
    """
    
    def __init__(self):
        self.service_name = "RFU_Hub_Theme_Security"
        self.master_key_name = "master_encryption_key"
        self.key_version = "v1"
        
    def get_master_key(self) -> bytes:
        """Get or create master encryption key"""
        try:
            # Try to retrieve existing key
            key_b64 = keyring.get_password(self.service_name, self.master_key_name)
            
            if key_b64:
                return base64.b64decode(key_b64)
            else:
                # Generate new master key
                return self._generate_and_store_master_key()
                
        except Exception as e:
            self.logger.error(f"Failed to get master key: {e}")
            # Fallback to file-based storage (less secure)
            return self._get_fallback_key()
    
    def _generate_and_store_master_key(self) -> bytes:
        """Generate and securely store new master key"""
        master_key = os.urandom(32)  # 256-bit key
        key_b64 = base64.b64encode(master_key).decode('utf-8')
        
        keyring.set_password(self.service_name, self.master_key_name, key_b64)
        return master_key
    
    def rotate_master_key(self) -> KeyRotationResult:
        """Rotate master encryption key"""
        # Implementation for key rotation with re-encryption of existing data
        pass
    
    def derive_theme_key(self, user_id: str, salt: bytes) -> bytes:
        """Derive theme-specific key using HKDF"""
        master_key = self.get_master_key()
        
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            info=f"theme_key_{user_id}".encode('utf-8'),
        )
        return hkdf.derive(master_key)
```

### 3. Integrity Validation and Corruption Detection

#### 3.1 ThemeIntegrityValidator

**File:** `src/rfu/core/theme_security/theme_validator.py`

```python
class ThemeIntegrityValidator:
    """
    Validates theme data integrity and detects various types of corruption
    including schema validation, data consistency, and format verification.
    """
    
    def __init__(self):
        self.schema_validator = ThemeSchemaValidator()
        self.checksum_validator = ThemeChecksumValidator()
        self.logger = logging.getLogger('RFU.ThemeIntegrityValidator')
    
    def validate_theme_integrity(self, theme_data: Dict[str, Any], 
                                expected_checksum: str = None) -> ValidationResult:
        """
        Comprehensive theme integrity validation
        
        Args:
            theme_data: Theme configuration data
            expected_checksum: Expected data checksum for verification
            
        Returns:
            ValidationResult with detailed validation information
        """
        validation_results = []
        
        # Schema validation
        schema_result = self.schema_validator.validate_schema(theme_data)
        validation_results.append(schema_result)
        
        # Checksum validation
        if expected_checksum:
            checksum_result = self.checksum_validator.validate_checksum(
                theme_data, expected_checksum
            )
            validation_results.append(checksum_result)
        
        # Data consistency validation
        consistency_result = self._validate_data_consistency(theme_data)
        validation_results.append(consistency_result)
        
        # Format validation
        format_result = self._validate_data_format(theme_data)
        validation_results.append(format_result)
        
        # Compile overall result
        overall_success = all(result.success for result in validation_results)
        
        return ValidationResult(
            success=overall_success,
            validation_details=validation_results,
            corruption_detected=not overall_success,
            corruption_type=self._determine_corruption_type(validation_results) if not overall_success else None
        )
    
    def detect_corruption_type(self, theme_data: Dict[str, Any]) -> CorruptionType:
        """Detect specific type of data corruption"""
        
        corruption_indicators = []
        
        # Check for truncated data
        if self._is_data_truncated(theme_data):
            corruption_indicators.append(CorruptionType.TRUNCATED)
        
        # Check for invalid characters
        if self._has_invalid_characters(theme_data):
            corruption_indicators.append(CorruptionType.INVALID_CHARACTERS)
        
        # Check for missing required fields
        if self._has_missing_required_fields(theme_data):
            corruption_indicators.append(CorruptionType.MISSING_FIELDS)
        
        # Check for invalid data types
        if self._has_invalid_data_types(theme_data):
            corruption_indicators.append(CorruptionType.INVALID_TYPES)
        
        return corruption_indicators[0] if corruption_indicators else CorruptionType.UNKNOWN
    
    def _validate_data_consistency(self, theme_data: Dict[str, Any]) -> ValidationResult:
        """Validate internal data consistency"""
        try:
            # Check color value consistency
            if 'colors' in theme_data:
                color_validation = self._validate_color_values(theme_data['colors'])
                if not color_validation.success:
                    return color_validation
            
            # Check font consistency
            if 'fonts' in theme_data:
                font_validation = self._validate_font_values(theme_data['fonts'])
                if not font_validation.success:
                    return font_validation
            
            # Check dimension consistency
            if 'dimensions' in theme_data:
                dimension_validation = self._validate_dimension_values(theme_data['dimensions'])
                if not dimension_validation.success:
                    return dimension_validation
            
            return ValidationResult(success=True, message="Data consistency validated")
            
        except Exception as e:
            return ValidationResult(success=False, message=f"Consistency validation failed: {e}")
    
    def _validate_color_values(self, colors: Dict[str, str]) -> ValidationResult:
        """Validate color value formats"""
        import re
        
        color_pattern = re.compile(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
        
        for color_name, color_value in colors.items():
            if not isinstance(color_value, str):
                return ValidationResult(
                    success=False, 
                    message=f"Color {color_name} must be a string"
                )
            
            if not color_pattern.match(color_value):
                return ValidationResult(
                    success=False, 
                    message=f"Invalid color format for {color_name}: {color_value}"
                )
        
        return ValidationResult(success=True, message="Color values validated")

class ThemeSchemaValidator:
    """Validates theme data against expected schema"""
    
    def __init__(self):
        self.schema = self._load_theme_schema()
    
    def validate_schema(self, theme_data: Dict[str, Any]) -> ValidationResult:
        """Validate theme data against schema"""
        try:
            import jsonschema
            jsonschema.validate(theme_data, self.schema)
            return ValidationResult(success=True, message="Schema validation passed")
        except jsonschema.ValidationError as e:
            return ValidationResult(success=False, message=f"Schema validation failed: {e.message}")
        except Exception as e:
            return ValidationResult(success=False, message=f"Schema validation error: {e}")
    
    def _load_theme_schema(self) -> Dict[str, Any]:
        """Load theme validation schema"""
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string", "minLength": 1, "maxLength": 100},
                "version": {"type": "string", "pattern": r"^\d+\.\d+\.\d+$"},
                "colors": {
                    "type": "object",
                    "properties": {
                        "primary": {"type": "string", "pattern": r"^#[0-9A-Fa-f]{6}$"},
                        "secondary": {"type": "string", "pattern": r"^#[0-9A-Fa-f]{6}$"},
                        "background": {"type": "string", "pattern": r"^#[0-9A-Fa-f]{6}$"},
                        "text": {"type": "string", "pattern": r"^#[0-9A-Fa-f]{6}$"}
                    },
                    "required": ["primary", "secondary", "background", "text"]
                },
                "fonts": {
                    "type": "object",
                    "properties": {
                        "family": {"type": "string", "minLength": 1},
                        "size": {"type": "integer", "minimum": 8, "maximum": 72},
                        "weight": {"type": "string", "enum": ["normal", "bold", "lighter", "bolder"]}
                    },
                    "required": ["family", "size"]
                },
                "dimensions": {
                    "type": "object",
                    "properties": {
                        "padding": {"type": "integer", "minimum": 0, "maximum": 100},
                        "margin": {"type": "integer", "minimum": 0, "maximum": 100},
                        "border_radius": {"type": "integer", "minimum": 0, "maximum": 50}
                    }
                }
            },
            "required": ["name", "version", "colors"]
        }

enum CorruptionType:
    TRUNCATED = "truncated"
    INVALID_CHARACTERS = "invalid_characters"
    MISSING_FIELDS = "missing_fields"
    INVALID_TYPES = "invalid_types"
    CHECKSUM_MISMATCH = "checksum_mismatch"
    UNKNOWN = "unknown"
```

### 4. Backup and Recovery System

#### 4.1 ThemeBackupManager

**File:** `src/rfu/core/theme_security/theme_backup.py`

```python
class ThemeBackupManager:
    """
    Manages automatic backup and recovery of theme data with
    versioning and integrity verification.
    """
    
    def __init__(self, database_manager: DatabaseManager):
        self.db_manager = database_manager
        self.backup_dir = Path('data/theme_backups')
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger('RFU.ThemeBackupManager')
    
    def create_theme_backup(self, user_id: str, theme_name: str, 
                           theme_data: Dict[str, Any]) -> BackupResult:
        """
        Create encrypted backup of theme data
        
        Args:
            user_id: User identifier
            theme_name: Theme name
            theme_data: Theme configuration data
            
        Returns:
            BackupResult with backup information
        """
        try:
            backup_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            # Create backup metadata
            backup_metadata = {
                'backup_id': backup_id,
                'user_id': user_id,
                'theme_name': theme_name,
                'created_at': timestamp,
                'version': '1.0',
                'checksum': self._calculate_checksum(theme_data)
            }
            
            # Encrypt backup data
            encryption_result = self._encrypt_backup_data({
                'metadata': backup_metadata,
                'theme_data': theme_data
            })
            
            if not encryption_result.success:
                return BackupResult(success=False, error=encryption_result.error)
            
            # Store backup file
            backup_filename = f"{user_id}_{theme_name}_{backup_id}.backup"
            backup_path = self.backup_dir / backup_filename
            
            with open(backup_path, 'wb') as f:
                f.write(encryption_result.encrypted_data)
            
            # Record backup in database
            self._record_backup_in_database(backup_metadata, str(backup_path))
            
            return BackupResult(
                success=True,
                backup_id=backup_id,
                backup_path=str(backup_path),
                checksum=backup_metadata['checksum']
            )
            
        except Exception as e:
            self.logger.error(f"Theme backup failed: {e}")
            return BackupResult(success=False, error=str(e))
    
    def restore_theme_from_backup(self, backup_id: str) -> RestoreResult:
        """
        Restore theme from backup with integrity verification
        
        Args:
            backup_id: Backup identifier
            
        Returns:
            RestoreResult with restored theme data
        """
        try:
            # Get backup information from database
            backup_info = self._get_backup_info(backup_id)
            if not backup_info:
                return RestoreResult(success=False, error="Backup not found")
            
            # Read backup file
            backup_path = Path(backup_info['file_path'])
            if not backup_path.exists():
                return RestoreResult(success=False, error="Backup file not found")
            
            with open(backup_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt backup data
            decryption_result = self._decrypt_backup_data(encrypted_data)
            if not decryption_result.success:
                return RestoreResult(success=False, error=decryption_result.error)
            
            backup_data = decryption_result.data
            
            # Verify backup integrity
            expected_checksum = backup_info['checksum']
            actual_checksum = self._calculate_checksum(backup_data['theme_data'])
            
            if expected_checksum != actual_checksum:
                return RestoreResult(
                    success=False, 
                    error="Backup integrity verification failed"
                )
            
            return RestoreResult(
                success=True,
                theme_data=backup_data['theme_data'],
                metadata=backup_data['metadata']
            )
            
        except Exception as e:
            self.logger.error(f"Theme restore failed: {e}")
            return RestoreResult(success=False, error=str(e))
    
    def cleanup_old_backups(self, retention_days: int = 30) -> CleanupResult:
        """Clean up old theme backups based on retention policy"""
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            # Get old backups from database
            old_backups = self.db_manager.execute_query("""
                SELECT backup_id, file_path FROM theme_backups 
                WHERE created_at < ?
            """, (cutoff_date.isoformat(),))
            
            cleaned_count = 0
            for backup in old_backups:
                try:
                    # Delete backup file
                    backup_path = Path(backup['file_path'])
                    if backup_path.exists():
                        backup_path.unlink()
                    
                    # Remove from database
                    self.db_manager.execute_update("""
                        DELETE FROM theme_backups WHERE backup_id = ?
                    """, (backup['backup_id'],))
                    
                    cleaned_count += 1
                    
                except Exception as e:
                    self.logger.warning(f"Failed to clean backup {backup['backup_id']}: {e}")
            
            return CleanupResult(success=True, cleaned_count=cleaned_count)
            
        except Exception as e:
            self.logger.error(f"Backup cleanup failed: {e}")
            return CleanupResult(success=False, error=str(e))
```

### 5. Access Control and Audit Logging

#### 5.1 ThemeAccessController

**File:** `src/rfu/core/theme_security/theme_access_control.py`

```python
class ThemeAccessController:
    """
    Controls access to theme data with user authentication,
    authorization, and rate limiting.
    """
    
    def __init__(self, database_manager: DatabaseManager):
        self.db_manager = database_manager
        self.rate_limiter = ThemeRateLimiter()
        self.session_manager = ThemeSessionManager()
        self.logger = logging.getLogger('RFU.ThemeAccessController')
    
    def authorize_theme_access(self, user_id: str, theme_name: str, 
                              operation: str, session_token: str = None) -> AuthorizationResult:
        """
        Authorize theme access with comprehensive security checks
        
        Args:
            user_id: User identifier
            theme_name: Theme name
            operation: Operation type ('read', 'write', 'delete', 'export')
            session_token: Optional session token for validation
            
        Returns:
            AuthorizationResult with access decision and metadata
        """
        try:
            # Validate session if token provided
            if session_token:
                session_validation = self.session_manager.validate_session(
                    user_id, session_token
                )
                if not session_validation.valid:
                    return AuthorizationResult(
                        authorized=False,
                        reason="Invalid session",
                        session_expired=session_validation.expired
                    )
            
            # Check rate limits
            rate_limit_result = self.rate_limiter.check_rate_limit(user_id, operation)
            if not rate_limit_result.allowed:
                return AuthorizationResult(
                    authorized=False,
                    reason="Rate limit exceeded",
                    retry_after=rate_limit_result.retry_after
                )
            
            # Check user permissions
            permission_result = self._check_user_permissions(user_id, theme_name, operation)
            if not permission_result.authorized:
                return AuthorizationResult(
                    authorized=False,
                    reason=permission_result.reason
                )
            
            # Check theme ownership/access rights
            ownership_result = self._check_theme_ownership(user_id, theme_name)
            if not ownership_result.authorized and operation in ['write', 'delete']:
                return AuthorizationResult(
                    authorized=False,
                    reason="Insufficient permissions for theme modification"
                )
            
            return AuthorizationResult(
                authorized=True,
                permissions=permission_result.permissions,
                session_valid=True
            )
            
        except Exception as e:
            self.logger.error(f"Authorization check failed: {e}")
            return AuthorizationResult(
                authorized=False,
                reason="Authorization system error"
            )
    
    def _check_user_permissions(self, user_id: str, theme_name: str, operation: str) -> PermissionResult:
        """Check user-specific permissions for theme operations"""
        
        # Get user permissions from database
        permissions = self.db_manager.execute_query("""
            SELECT permission_type, is_active, expires_at 
            FROM theme_permissions 
            WHERE user_id = ? AND (theme_name = ? OR theme_name = '*')
            AND is_active = TRUE
        """, (user_id, theme_name))
        
        # Check if user has required permission
        required_permission = self._map_operation_to_permission(operation)
        
        for perm in permissions:
            if perm['permission_type'] == required_permission or perm['permission_type'] == 'admin':
                # Check expiration
                if perm['expires_at']:
                    expires_at = datetime.fromisoformat(perm['expires_at'])
                    if datetime.now() > expires_at:
                        continue
                
                return PermissionResult(
                    authorized=True,
                    permissions=[perm['permission_type']]
                )
        
        return PermissionResult(
            authorized=False,
            reason=f"User lacks {required_permission} permission"
        )

class ThemeRateLimiter:
    """Rate limiting for theme operations to prevent abuse"""
    
    def __init__(self):
        self.rate_limits = {
            'read': {'requests': 100, 'window': 3600},    # 100 reads per hour
            'write': {'requests': 20, 'window': 3600},    # 20 writes per hour
            'delete': {'requests': 5, 'window': 3600},    # 5 deletes per hour
            'export': {'requests': 10, 'window': 3600}    # 10 exports per hour
        }
        self.request_history = {}
    
    def check_rate_limit(self, user_id: str, operation: str) -> RateLimitResult:
        """Check if user has exceeded rate limit for operation"""
        
        if operation not in self.rate_limits:
            return RateLimitResult(allowed=True)
        
        limit_config = self.rate_limits[operation]
        current_time = time.time()
        window_start = current_time - limit_config['window']
        
        # Get user's request history for this operation
        user_key = f"{user_id}:{operation}"
        if user_key not in self.request_history:
            self.request_history[user_key] = []
        
        # Clean old requests outside window
        self.request_history[user_key] = [
            req_time for req_time in self.request_history[user_key]
            if req_time > window_start
        ]
        
        # Check if limit exceeded
        if len(self.request_history[user_key]) >= limit_config['requests']:
            oldest_request = min(self.request_history[user_key])
            retry_after = oldest_request + limit_config['window'] - current_time
            
            return RateLimitResult(
                allowed=False,
                retry_after=max(0, retry_after)
            )
        
        # Record this request
        self.request_history[user_key].append(current_time)
        
        return RateLimitResult(allowed=True)
```

### 6. Database Schema for Theme Security

#### 6.1 Secure Theme Storage Tables

```sql
-- Secure theme storage with encryption
CREATE TABLE IF NOT EXISTS secure_themes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL DEFAULT 'default',
    theme_name TEXT NOT NULL,
    encrypted_data BLOB NOT NULL,
    salt BLOB NOT NULL,
    nonce BLOB NOT NULL,
    integrity_hash TEXT NOT NULL,
    encryption_version INTEGER DEFAULT 1,
    theme_version TEXT DEFAULT '1.0',
    data_size_bytes INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP,
    backup_count INTEGER DEFAULT 0,
    corruption_detected BOOLEAN DEFAULT FALSE,
    last_validation TIMESTAMP,
    UNIQUE(user_id, theme_name)
);

-- Theme access audit log
CREATE TABLE IF NOT EXISTS theme_access_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    theme_name TEXT NOT NULL,
    operation TEXT NOT NULL CHECK (operation IN ('read', 'write', 'delete', 'export', 'import', 'validate')),
    ip_address TEXT,
    user_agent TEXT,
    session_id TEXT,