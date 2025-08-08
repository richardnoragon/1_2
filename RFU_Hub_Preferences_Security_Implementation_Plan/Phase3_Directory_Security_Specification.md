# Phase 3: Directory Preferences Security Controls and PII Protection

## Technical Specification

### Overview

This specification details the implementation of robust security controls and permission management for directory preferences functionality to prevent exposure of Personally Identifiable Information (PII). The system includes access control validation, path sanitization, user permission verification, and secure directory handling with appropriate encryption and audit logging.

## Architecture Components

### 1. Directory Security Framework

#### 1.1 DirectorySecurityManager

**File:** `src/rfu/core/directory_security/directory_security_manager.py`

```python
class DirectorySecurityManager:
    """
    Central manager for directory security operations including path validation,
    PII protection, access control, and comprehensive audit logging.
    """
    
    def __init__(self, database_manager: DatabaseManager):
        self.db_manager = database_manager
        self.path_validator = DirectoryPathValidator()
        self.pii_detector = PIIDetector()
        self.permission_manager = DirectoryPermissionManager(database_manager)
        self.access_controller = DirectoryAccessController(database_manager)
        self.audit_logger = DirectoryAuditLogger(database_manager)
        self.encryption = DirectoryPathEncryption()
        self.sanitizer = PathSanitizer()
        self.logger = logging.getLogger('RFU.DirectorySecurityManager')
    
    def store_directory_preference(self, user_id: str, tool_name: str, 
                                  directory_type: str, directory_path: str) -> DirectoryStorageResult:
        """
        Store directory preference with comprehensive security validation
        
        Args:
            user_id: User identifier
            tool_name: Tool requesting directory storage
            directory_type: Type of directory ('favorite', 'recent', 'default')
            directory_path: Directory path to store
            
        Returns:
            DirectoryStorageResult with storage outcome and security metadata
        """
        try:
            # Sanitize and validate path
            sanitized_path = self.sanitizer.sanitize_path(directory_path)
            validation_result = self.path_validator.validate_directory_path(
                sanitized_path, user_id
            )
            
            if not validation_result.valid:
                return DirectoryStorageResult(
                    success=False,
                    error=f"Path validation failed: {validation_result.reason}",
                    security_violation=True
                )
            
            # Check permissions
            permission_result = self.permission_manager.check_directory_permission(
                user_id, sanitized_path, 'write'
            )
            
            if not permission_result.authorized:
                self.audit_logger.log_access_denied(
                    user_id, sanitized_path, 'write', permission_result.reason
                )
                return DirectoryStorageResult(
                    success=False,
                    error=f"Access denied: {permission_result.reason}",
                    security_violation=True
                )
            
            # Detect PII sensitivity
            pii_result = self.pii_detector.analyze_directory_path(sanitized_path)
            
            # Encrypt path if PII sensitive
            if pii_result.contains_pii or pii_result.sensitivity_level >= 3:
                encryption_result = self.encryption.encrypt_directory_path(
                    sanitized_path, user_id
                )
                
                if not encryption_result.success:
                    return DirectoryStorageResult(
                        success=False,
                        error="Failed to encrypt sensitive directory path"
                    )
                
                encrypted_path = encryption_result.encrypted_data
                path_hash = encryption_result.path_hash
            else:
                encrypted_path = sanitized_path.encode('utf-8')
                path_hash = self._create_path_hash(sanitized_path)
            
            # Store in database
            storage_result = self._store_encrypted_directory(
                user_id, tool_name, directory_type, encrypted_path, 
                path_hash, pii_result.contains_pii, pii_result.sensitivity_level
            )
            
            # Log successful storage
            self.audit_logger.log_directory_operation(
                user_id, path_hash, 'store', True, {
                    'tool_name': tool_name,
                    'directory_type': directory_type,
                    'pii_sensitive': pii_result.contains_pii,
                    'sensitivity_level': pii_result.sensitivity_level
                }
            )
            
            return DirectoryStorageResult(
                success=True,
                path_hash=path_hash,
                pii_sensitive=pii_result.contains_pii,
                sensitivity_level=pii_result.sensitivity_level
            )
            
        except Exception as e:
            self.logger.error(f"Directory storage failed: {e}")
            return DirectoryStorageResult(
                success=False,
                error=f"Storage system error: {e}"
            )
    
    def retrieve_directory_preference(self, user_id: str, path_hash: str) -> DirectoryRetrievalResult:
        """
        Retrieve directory preference with security validation and decryption
        
        Args:
            user_id: User identifier
            path_hash: Hashed directory identifier
            
        Returns:
            DirectoryRetrievalResult with decrypted path or error
        """
        try:
            # Check read permissions
            permission_result = self.permission_manager.check_directory_permission(
                user_id, path_hash, 'read'
            )
            
            if not permission_result.authorized:
                self.audit_logger.log_access_denied(
                    user_id, path_hash, 'read', permission_result.reason
                )
                return DirectoryRetrievalResult(
                    success=False,
                    error=f"Access denied: {permission_result.reason}",
                    security_violation=True
                )
            
            # Retrieve encrypted directory data
            directory_data = self._get_encrypted_directory(user_id, path_hash)
            
            if not directory_data:
                return DirectoryRetrievalResult(
                    success=False,
                    error="Directory preference not found"
                )
            
            # Decrypt path if encrypted
            if directory_data['is_pii_sensitive']:
                decryption_result = self.encryption.decrypt_directory_path(
                    directory_data['encrypted_path'], user_id
                )
                
                if not decryption_result.success:
                    return DirectoryRetrievalResult(
                        success=False,
                        error="Failed to decrypt directory path"
                    )
                
                directory_path = decryption_result.directory_path
            else:
                directory_path = directory_data['encrypted_path'].decode('utf-8')
            
            # Validate path still exists and is accessible
            if not self.path_validator.validate_path_accessibility(directory_path):
                self.audit_logger.log_directory_operation(
                    user_id, path_hash, 'access_validation_failed', False, {
                        'reason': 'Path no longer accessible'
                    }
                )
                return DirectoryRetrievalResult(
                    success=False,
                    error="Directory path is no longer accessible",
                    path_inaccessible=True
                )
            
            # Log successful retrieval
            self.audit_logger.log_directory_operation(
                user_id, path_hash, 'retrieve', True, {
                    'tool_name': directory_data['tool_name'],
                    'directory_type': directory_data['directory_type']
                }
            )
            
            return DirectoryRetrievalResult(
                success=True,
                directory_path=directory_path,
                tool_name=directory_data['tool_name'],
                directory_type=directory_data['directory_type'],
                pii_sensitive=directory_data['is_pii_sensitive'],
                sensitivity_level=directory_data['sensitivity_level']
            )
            
        except Exception as e:
            self.logger.error(f"Directory retrieval failed: {e}")
            return DirectoryRetrievalResult(
                success=False,
                error=f"Retrieval system error: {e}"
            )

@dataclass
class DirectoryStorageResult:
    success: bool
    path_hash: Optional[str] = None
    pii_sensitive: bool = False
    sensitivity_level: int = 0
    error: Optional[str] = None
    security_violation: bool = False

@dataclass
class DirectoryRetrievalResult:
    success: bool
    directory_path: Optional[str] = None
    tool_name: Optional[str] = None
    directory_type: Optional[str] = None
    pii_sensitive: bool = False
    sensitivity_level: int = 0
    error: Optional[str] = None
    security_violation: bool = False
    path_inaccessible: bool = False
```

### 2. Path Validation and Sanitization

#### 2.1 DirectoryPathValidator

**File:** `src/rfu/core/directory_security/directory_validator.py`

```python
class DirectoryPathValidator:
    """
    Validates directory paths for security vulnerabilities including
    path traversal attacks, symbolic link exploitation, and access violations.
    """
    
    def __init__(self):
        self.allowed_path_patterns = self._load_allowed_patterns()
        self.blocked_path_patterns = self._load_blocked_patterns()
        self.max_path_length = 4096
        self.max_depth = 50
        self.logger = logging.getLogger('RFU.DirectoryPathValidator')
    
    def validate_directory_path(self, directory_path: str, user_id: str) -> PathValidationResult:
        """
        Comprehensive directory path validation
        
        Args:
            directory_path: Directory path to validate
            user_id: User identifier for context-specific validation
            
        Returns:
            PathValidationResult with validation outcome and details
        """
        try:
            # Basic format validation
            format_result = self._validate_path_format(directory_path)
            if not format_result.valid:
                return format_result
            
            # Path traversal validation
            traversal_result = self._validate_path_traversal(directory_path)
            if not traversal_result.valid:
                return traversal_result
            
            # Symbolic link validation
            symlink_result = self._validate_symbolic_links(directory_path)
            if not symlink_result.valid:
                return symlink_result
            
            # Network path validation
            network_result = self._validate_network_paths(directory_path)
            if not network_result.valid:
                return network_result
            
            # User-specific validation
            user_result = self._validate_user_access_rights(directory_path, user_id)
            if not user_result.valid:
                return user_result
            
            # Whitelist/blacklist validation
            pattern_result = self._validate_against_patterns(directory_path)
            if not pattern_result.valid:
                return pattern_result
            
            return PathValidationResult(
                valid=True,
                normalized_path=os.path.normpath(directory_path),
                security_level=self._calculate_security_level(directory_path)
            )
            
        except Exception as e:
            self.logger.error(f"Path validation error: {e}")
            return PathValidationResult(
                valid=False,
                reason=f"Validation system error: {e}"
            )
    
    def _validate_path_format(self, directory_path: str) -> PathValidationResult:
        """Validate basic path format and constraints"""
        
        # Check path length
        if len(directory_path) > self.max_path_length:
            return PathValidationResult(
                valid=False,
                reason=f"Path exceeds maximum length of {self.max_path_length} characters"
            )
        
        # Check for null bytes
        if '\x00' in directory_path:
            return PathValidationResult(
                valid=False,
                reason="Path contains null bytes"
            )
        
        # Check for invalid characters
        invalid_chars = ['<', '>', '|', '*', '?']
        if any(char in directory_path for char in invalid_chars):
            return PathValidationResult(
                valid=False,
                reason=f"Path contains invalid characters: {invalid_chars}"
            )
        
        # Check path depth
        path_depth = len(Path(directory_path).parts)
        if path_depth > self.max_depth:
            return PathValidationResult(
                valid=False,
                reason=f"Path depth exceeds maximum of {self.max_depth} levels"
            )
        
        return PathValidationResult(valid=True)
    
    def _validate_path_traversal(self, directory_path: str) -> PathValidationResult:
        """Validate against path traversal attacks"""
        
        # Normalize path and check for traversal patterns
        normalized = os.path.normpath(directory_path)
        
        # Check for directory traversal sequences
        traversal_patterns = ['../', '..\\', '../', '..\\\\']
        for pattern in traversal_patterns:
            if pattern in directory_path:
                return PathValidationResult(
                    valid=False,
                    reason="Path contains directory traversal sequences"
                )
        
        # Check if normalized path goes outside allowed boundaries
        if normalized.startswith('..'):
            return PathValidationResult(
                valid=False,
                reason="Path attempts to access parent directories"
            )
        
        # Check for encoded traversal attempts
        encoded_patterns = ['%2e%2e', '%2E%2E', '..%2f', '..%5c']
        for pattern in encoded_patterns:
            if pattern.lower() in directory_path.lower():
                return PathValidationResult(
                    valid=False,
                    reason="Path contains encoded traversal sequences"
                )
        
        return PathValidationResult(valid=True)
    
    def _validate_symbolic_links(self, directory_path: str) -> PathValidationResult:
        """Validate symbolic links for security risks"""
        
        try:
            path_obj = Path(directory_path)
            
            # Check if path exists and resolve symbolic links
            if path_obj.exists():
                resolved_path = path_obj.resolve()
                
                # Check if resolved path is different (indicates symlink)
                if str(resolved_path) != str(path_obj.absolute()):
                    # Validate that symlink target is safe
                    if not self._is_symlink_target_safe(resolved_path):
                        return PathValidationResult(
                            valid=False,
                            reason="Symbolic link target is not safe"
                        )
            
            return PathValidationResult(valid=True)
            
        except (OSError, RuntimeError) as e:
            return PathValidationResult(
                valid=False,
                reason=f"Symbolic link validation failed: {e}"
            )
    
    def _validate_network_paths(self, directory_path: str) -> PathValidationResult:
        """Validate network paths for security"""
        
        # Check for UNC paths (Windows)
        if directory_path.startswith('\\\\'):
            return PathValidationResult(
                valid=False,
                reason="UNC network paths are not allowed"
            )
        
        # Check for network protocols
        network_protocols = ['ftp://', 'http://', 'https://', 'smb://', 'nfs://']
        for protocol in network_protocols:
            if directory_path.lower().startswith(protocol):
                return PathValidationResult(
                    valid=False,
                    reason=f"Network protocol paths are not allowed: {protocol}"
                )
        
        return PathValidationResult(valid=True)
    
    def _validate_user_access_rights(self, directory_path: str, user_id: str) -> PathValidationResult:
        """Validate user has appropriate access rights"""
        
        try:
            path_obj = Path(directory_path)
            
            # Check if path exists
            if not path_obj.exists():
                return PathValidationResult(valid=True)  # Allow non-existent paths for creation
            
            # Check read access
            if not os.access(directory_path, os.R_OK):
                return PathValidationResult(
                    valid=False,
                    reason="User lacks read access to directory"
                )
            
            # Check if path is within user's allowed directories
            if not self._is_path_in_user_scope(directory_path, user_id):
                return PathValidationResult(
                    valid=False,
                    reason="Directory is outside user's allowed scope"
                )
            
            return PathValidationResult(valid=True)
            
        except Exception as e:
            return PathValidationResult(
                valid=False,
                reason=f"Access rights validation failed: {e}"
            )
    
    def _load_allowed_patterns(self) -> List[str]:
        """Load allowed directory path patterns"""
        return [
            r'^[A-Za-z]:\\Users\\[^\\]+\\.*',  # Windows user directories
            r'^/home/[^/]+/.*',                # Linux user directories
            r'^/Users/[^/]+/.*',               # macOS user directories
            r'^[A-Za-z]:\\Program Files\\.*',  # Windows program files
            r'^/opt/.*',                       # Linux optional software
            r'^/usr/local/.*',                 # Linux local software
        ]
    
    def _load_blocked_patterns(self) -> List[str]:
        """Load blocked directory path patterns"""
        return [
            r'^[A-Za-z]:\\Windows\\System32\\.*',  # Windows system directories
            r'^/etc/.*',                           # Linux system configuration
            r'^/root/.*',                          # Linux root directory
            r'^/sys/.*',                           # Linux system files
            r'^/proc/.*',                          # Linux process files
            r'^[A-Za-z]:\\System Volume Information\\.*',  # Windows system info
        ]

@dataclass
class PathValidationResult:
    valid: bool
    reason: Optional[str] = None
    normalized_path: Optional[str] = None
    security_level: int = 0
```

#### 2.2 PathSanitizer

**File:** `src/rfu/core/directory_security/path_sanitizer.py`

```python
class PathSanitizer:
    """
    Sanitizes directory paths to prevent security vulnerabilities
    while preserving functionality.
    """
    
    def __init__(self):
        self.replacement_char = '_'
        self.max_component_length = 255
        self.logger = logging.getLogger('RFU.PathSanitizer')
    
    def sanitize_path(self, directory_path: str) -> str:
        """
        Sanitize directory path for safe storage and usage
        
        Args:
            directory_path: Raw directory path
            
        Returns:
            Sanitized directory path
        """
        try:
            # Remove null bytes
            sanitized = directory_path.replace('\x00', '')
            
            # Remove control characters
            sanitized = ''.join(char for char in sanitized if ord(char) >= 32)
            
            # Replace dangerous characters
            dangerous_chars = ['<', '>', '|', '*', '?', '"']
            for char in dangerous_chars:
                sanitized = sanitized.replace(char, self.replacement_char)
            
            # Normalize path separators
            sanitized = sanitized.replace('\\', os.sep).replace('/', os.sep)
            
            # Remove multiple consecutive separators
            while os.sep + os.sep in sanitized:
                sanitized = sanitized.replace(os.sep + os.sep, os.sep)
            
            # Remove leading/trailing whitespace from components
            components = sanitized.split(os.sep)
            components = [comp.strip() for comp in components]
            
            # Limit component length
            components = [
                comp[:self.max_component_length] if len(comp) > self.max_component_length else comp
                for comp in components
            ]
            
            # Remove empty components (except for root)
            if len(components) > 1:
                components = [comp for comp in components if comp]
            
            # Reconstruct path
            sanitized = os.sep.join(components)
            
            # Normalize the final path
            sanitized = os.path.normpath(sanitized)
            
            return sanitized
            
        except Exception as e:
            self.logger.error(f"Path sanitization failed: {e}")
            return directory_path  # Return original if sanitization fails
    
    def sanitize_for_display(self, directory_path: str) -> str:
        """
        Sanitize path for safe display in UI (additional anonymization)
        
        Args:
            directory_path: Directory path to sanitize for display
            
        Returns:
            Display-safe directory path
        """
        try:
            # Basic sanitization
            sanitized = self.sanitize_path(directory_path)
            
            # Replace user-specific information
            sanitized = self._anonymize_user_info(sanitized)
            
            # Truncate very long paths for display
            if len(sanitized) > 100:
                sanitized = sanitized[:50] + '...' + sanitized[-47:]
            
            return sanitized
            
        except Exception as e:
            self.logger.error(f"Display sanitization failed: {e}")
            return "***SANITIZATION_ERROR***"
    
    def _anonymize_user_info(self, path: str) -> str:
        """Anonymize user-specific information in paths"""
        
        # Replace username in common patterns
        import re
        
        # Windows user paths
        path = re.sub(r'\\Users\\[^\\]+\\', '\\Users\\[USER]\\', path)
        
        # Linux/macOS user paths
        path = re.sub(r'/home/[^/]+/', '/home/[USER]/', path)
        path = re.sub(r'/Users/[^/]+/', '/Users/[USER]/', path)
        
        return path
```

### 3. PII Detection and Protection

#### 3.1 PIIDetector

**File:** `src/rfu/core/directory_security/pii_detector.py`

```python
class PIIDetector:
    """
    Detects Personally Identifiable Information in directory paths
    and assigns appropriate sensitivity levels.
    """
    
    def __init__(self):
        self.pii_patterns = self._load_pii_patterns()
        self.sensitivity_rules = self._load_sensitivity_rules()
        self.logger = logging.getLogger('RFU.PIIDetector')
    
    def analyze_directory_path(self, directory_path: str) -> PIIAnalysisResult:
        """
        Analyze directory path for PII content and sensitivity
        
        Args:
            directory_path: Directory path to analyze
            
        Returns:
            PIIAnalysisResult with PII detection and sensitivity information
        """
        try:
            # Normalize path for analysis
            normalized_path = directory_path.lower().replace('\\', '/')
            
            # Check for PII patterns
            pii_indicators = []
            for pattern_name, pattern_regex in self.pii_patterns.items():
                if re.search(pattern_regex, normalized_path):
                    pii_indicators.append(pattern_name)
            
            # Calculate sensitivity level
            sensitivity_level = self._calculate_sensitivity_level(pii_indicators, normalized_path)
            
            # Determine if path contains PII
            contains_pii = len(pii_indicators) > 0 or sensitivity_level >= 3
            
            # Generate anonymized version for logging
            anonymized_path = self._create_anonymized_path(directory_path, pii_indicators)
            
            return PIIAnalysisResult(
                contains_pii=contains_pii,
                sensitivity_level=sensitivity_level,
                pii_indicators=pii_indicators,
                anonymized_path=anonymized_path,
                requires_encryption=sensitivity_level >= 3
            )
            
        except Exception as e:
            self.logger.error(f"PII analysis failed: {e}")
            return PIIAnalysisResult(
                contains_pii=True,  # Err on the side of caution
                sensitivity_level=5,
                pii_indicators=['analysis_error'],
                anonymized_path='***ERROR***',
                requires_encryption=True
            )
    
    def _load_pii_patterns(self) -> Dict[str, str]:
        """Load PII detection patterns"""
        return {
            'username_directory': r'/(?:users?|home)/([^/]+)/',
            'personal_documents': r'/(?:documents?|my documents?|personal)/',
            'desktop_directory': r'/desktop/',
            'downloads_directory': r'/downloads?/',
            'pictures_directory': r'/(?:pictures?|photos?|images?)/',
            'videos_directory': r'/(?:videos?|movies?)/',
            'music_directory': r'/(?:music|audio)/',
            'email_directory': r'/(?:mail|email|outlook|thunderbird)/',
            'browser_data': r'/(?:chrome|firefox|safari|edge|browser)/',
            'social_security': r'/(?:ssn|social.?security)/',
            'financial_data': r'/(?:bank|finance|tax|irs|financial)/',
            'medical_records': r'/(?:medical|health|doctor|hospital)/',
            'legal_documents': r'/(?:legal|lawyer|attorney|court)/',
            'private_keys': r'/(?:\.ssh|\.gnupg|keys?|certificates?)/',
            'backup_data': r'/(?:backup|restore|archive)/',
            'cloud_sync': r'/(?:dropbox|onedrive|google.?drive|icloud)/',
        }
    
    def _load_sensitivity_rules(self) -> Dict[str, int]:
        """Load sensitivity level rules"""
        return {
            'username_directory': 2,
            'personal_documents': 4,
            'desktop_directory': 3,
            'downloads_directory': 2,
            'pictures_directory': 3,
            'videos_directory': 3,
            'music_directory': 2,
            'email_directory': 5,
            'browser_data': 4,
            'social_security': 5,
            'financial_data': 5,
            'medical_records': 5,
            'legal_documents': 4,
            'private_keys': 5,
            'backup_data': 3,
            'cloud_sync': 3,
        }
    
    def _calculate_sensitivity_level(self, pii_indicators: List[str], path: str) -> int:
        """Calculate overall sensitivity level"""
        
        if not pii_indicators:
            return 1  # Low sensitivity
        
        # Get maximum sensitivity from indicators
        max_sensitivity = max(
            self.sensitivity_rules.get(indicator, 1) 
            for indicator in pii_indicators
        )
        
        # Increase sensitivity for multiple indicators
        if len(pii_indicators) > 2:
            max_sensitivity = min(5, max_sensitivity + 1)
        
        # Check for additional sensitive patterns
        if any(keyword in path for keyword in ['private', 'confidential', 'secret']):
            max_sensitivity = min(5, max_sensitivity + 1)
        
        return max_sensitivity
    
    def _create_anonymized_path(self, directory_path: str, pii_indicators: List[str]) -> str:
        """Create anonymized version of path for logging"""
        
        anonymized = directory_path.lower()
        
        # Replace usernames
        anonymized = re.sub(r'/(?:users?|home)/[^/]+/', '/[USER]/', anonymized)
        anonymized = re.sub(r'\\users\\[^\\]+\\', '\\[USER]\\', anonymized)
        
        # Replace other PII patterns
        for indicator in pii_indicators:
            if indicator == 'personal_documents':
                anonymized = re.sub(r'/(?:documents?|my documents?|personal)/', '/[DOCS]/', anonymized)
            elif indicator == 'email_directory':
                anonymized = re.sub(r'/(?:mail|email|outlook|thunderbird)/', '/[EMAIL]/', anonymized)
            elif indicator == 'financial_data':
                anonymized = re.sub(r'/(?:bank|finance|tax|irs|financial)/', '/[FINANCIAL]/', anonymized)
            elif indicator == 'medical_records':
                anonymized = re.sub(r'/(?:medical|health|doctor|hospital)/', '/[MEDICAL]/', anonymized)
        
        # Replace any remaining potentially sensitive directory names
        components = anonymized.split('/')
        anonymized_components = []
        
        for component in components:
            if len(component) > 20:  # Long directory names might contain PII
                anonymized_components.append('[LONG_NAME]')
            elif any(char.isdigit() for char in component) and len(component) > 8:
                anonymized_components.append('[NUMERIC_NAME]')
            else:
                anonymized_components.append(component)
        
        return '/'.join(anonymized_components)

@dataclass
class PIIAnalysisResult:
    contains_pii: bool
    sensitivity_level: int
    pii_indicators: List[str]
    anonymized_path: str
    requires_encryption: bool
```

### 4. Directory Path Encryption

#### 4.1 DirectoryPathEncryption

**File:** `src/rfu/core/directory_security/directory_encryption.py`

```python
class DirectoryPathEncryption:
    """
    Handles encryption and decryption of directory paths with
    user-specific key derivation and integrity protection.
    """
    
    def __init__(self):
        self.key_manager = DirectoryKeyManager()
        self.salt_length = 32
        self.nonce_length = 12
        self.key_iterations = 100000
        self.logger = logging.getLogger('RFU.DirectoryPathEncryption')
    
    def encrypt_directory_path(self, directory_path: str, user_id: str) -> DirectoryEncryptionResult:
        """
        Encrypt directory path with user-specific key
        
        Args:
            directory_path: Directory path to encrypt
            user_id: User identifier for key derivation
            
        Returns:
            DirectoryEncryptionResult with encrypted data and metadata
        """
        try:
            # Normalize path for consistent encryption
            normalized_path = os.path.normpath(directory_path)
            path_bytes = normalized_path.encode('utf-8')
            
            # Generate salt and derive key
            salt = os.urandom(self.salt_length)
            key = self._derive_directory_key(user_id, salt)
            
            # Generate nonce for AEAD
            nonce = os.urandom(self.nonce_length)
            
            # Encrypt with AES-GCM
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            aesgcm = AESGCM(key)
            encrypted_data = aesgcm.encrypt(nonce, path_bytes, None)
            
            # Create path hash for indexing (without revealing path)
            path_hash = self._create_secure_path_hash(normalized_path, user_id)
            
            # Create integrity hash
            integrity_hash = self._create_integrity_hash(encrypted_data, salt, nonce)
            
            return DirectoryEncryptionResult(
                success=True,
                encrypted_data=encrypted_data,
                salt=salt,
                nonce=nonce,
                path_hash=path_hash,
                integrity_hash=integrity_hash,
                encryption_version=1
            )
            
        except Exception as e:
            self.logger.error(f"Directory path encryption failed: {e}")
            return DirectoryEncryptionResult(
                success=False,
                error=f"Encryption failed: {e}"
            )
    
    def decrypt_directory_path(self, encrypted_data: bytes, salt: bytes, 
                              nonce: bytes