# Phase 2: Theme Data Privacy Protection and Corruption Handling - Complete Specification

## Database Schema for Theme Security (Continued)

```sql
-- Theme access audit log
CREATE TABLE IF NOT EXISTS theme_access_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    theme_name TEXT NOT NULL,
    operation TEXT NOT NULL CHECK (operation IN ('read', 'write', 'delete', 'export', 'import', 'validate')),
    ip_address TEXT,
    user_agent TEXT,
    session_id TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    data_size_bytes INTEGER,
    execution_time_ms INTEGER,
    security_level TEXT DEFAULT 'normal' CHECK (security_level IN ('low', 'normal', 'high', 'critical'))
);

-- Theme permissions management
CREATE TABLE IF NOT EXISTS theme_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    theme_name TEXT NOT NULL, -- '*' for all themes
    permission_type TEXT NOT NULL CHECK (permission_type IN ('read', 'write', 'delete', 'export', 'admin')),
    granted_by TEXT NOT NULL,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    conditions TEXT, -- JSON conditions for conditional access
    UNIQUE(user_id, theme_name, permission_type)
);

-- Theme backups tracking
CREATE TABLE IF NOT EXISTS theme_backups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    backup_id TEXT NOT NULL UNIQUE,
    user_id TEXT NOT NULL,
    theme_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    checksum TEXT NOT NULL,
    encryption_version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    backup_type TEXT DEFAULT 'automatic' CHECK (backup_type IN ('automatic', 'manual', 'corruption_recovery')),
    compression_type TEXT DEFAULT 'gzip'
);

-- Theme corruption incidents
CREATE TABLE IF NOT EXISTS theme_corruption_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    theme_name TEXT NOT NULL,
    corruption_type TEXT NOT NULL,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    corruption_details TEXT, -- JSON details about corruption
    recovery_attempted BOOLEAN DEFAULT FALSE,
    recovery_successful BOOLEAN DEFAULT FALSE,
    recovery_method TEXT,
    data_loss_occurred BOOLEAN DEFAULT FALSE,
    backup_used TEXT -- backup_id if backup was used for recovery
);

-- Encryption keys management
CREATE TABLE IF NOT EXISTS theme_encryption_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_id TEXT NOT NULL UNIQUE,
    key_type TEXT NOT NULL CHECK (key_type IN ('master', 'user', 'backup')),
    encrypted_key BLOB NOT NULL,
    salt BLOB NOT NULL,
    key_version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    rotation_count INTEGER DEFAULT 0,
    last_used TIMESTAMP
);
```

## Error Recovery and Corruption Handling

### 7.1 ThemeRecoveryManager

**File:** `src/rfu/core/theme_security/theme_recovery.py`

```python
class ThemeRecoveryManager:
    """
    Handles theme data recovery from various corruption scenarios
    with automatic fallback mechanisms and data preservation.
    """
    
    def __init__(self, database_manager: DatabaseManager):
        self.db_manager = database_manager
        self.backup_manager = ThemeBackupManager(database_manager)
        self.validator = ThemeIntegrityValidator()
        self.logger = logging.getLogger('RFU.ThemeRecoveryManager')
    
    def recover_corrupted_theme(self, user_id: str, theme_name: str, 
                               corruption_type: CorruptionType) -> RecoveryResult:
        """
        Recover corrupted theme using appropriate recovery strategy
        
        Args:
            user_id: User identifier
            theme_name: Corrupted theme name
            corruption_type: Type of corruption detected
            
        Returns:
            RecoveryResult with recovery outcome and details
        """
        try:
            # Log corruption incident
            self._log_corruption_incident(user_id, theme_name, corruption_type)
            
            # Determine recovery strategy based on corruption type
            recovery_strategy = self._determine_recovery_strategy(corruption_type)
            
            # Execute recovery
            recovery_result = self._execute_recovery_strategy(
                user_id, theme_name, recovery_strategy
            )
            
            # Validate recovered data
            if recovery_result.success:
                validation_result = self.validator.validate_theme_integrity(
                    recovery_result.recovered_data
                )
                
                if not validation_result.success:
                    # Recovery failed validation, try next strategy
                    return self._try_fallback_recovery(user_id, theme_name)
            
            # Update corruption log with recovery outcome
            self._update_corruption_log(
                user_id, theme_name, recovery_result.success, 
                recovery_strategy, recovery_result.data_loss
            )
            
            return recovery_result
            
        except Exception as e:
            self.logger.error(f"Theme recovery failed: {e}")
            return RecoveryResult(
                success=False,
                error=f"Recovery system error: {e}",
                recovery_strategy="error_fallback"
            )
    
    def _determine_recovery_strategy(self, corruption_type: CorruptionType) -> RecoveryStrategy:
        """Determine optimal recovery strategy based on corruption type"""
        
        strategy_map = {
            CorruptionType.TRUNCATED: RecoveryStrategy.BACKUP_RESTORE,
            CorruptionType.INVALID_CHARACTERS: RecoveryStrategy.DATA_SANITIZATION,
            CorruptionType.MISSING_FIELDS: RecoveryStrategy.FIELD_RECONSTRUCTION,
            CorruptionType.INVALID_TYPES: RecoveryStrategy.TYPE_CORRECTION,
            CorruptionType.CHECKSUM_MISMATCH: RecoveryStrategy.BACKUP_RESTORE,
            CorruptionType.UNKNOWN: RecoveryStrategy.FULL_BACKUP_RESTORE
        }
        
        return strategy_map.get(corruption_type, RecoveryStrategy.DEFAULT_FALLBACK)
    
    def _execute_recovery_strategy(self, user_id: str, theme_name: str, 
                                  strategy: RecoveryStrategy) -> RecoveryResult:
        """Execute specific recovery strategy"""
        
        if strategy == RecoveryStrategy.BACKUP_RESTORE:
            return self._recover_from_backup(user_id, theme_name)
        
        elif strategy == RecoveryStrategy.DATA_SANITIZATION:
            return self._sanitize_corrupted_data(user_id, theme_name)
        
        elif strategy == RecoveryStrategy.FIELD_RECONSTRUCTION:
            return self._reconstruct_missing_fields(user_id, theme_name)
        
        elif strategy == RecoveryStrategy.TYPE_CORRECTION:
            return self._correct_data_types(user_id, theme_name)
        
        elif strategy == RecoveryStrategy.DEFAULT_FALLBACK:
            return self._restore_default_theme(user_id, theme_name)
        
        else:
            return RecoveryResult(
                success=False,
                error=f"Unknown recovery strategy: {strategy}"
            )
    
    def _recover_from_backup(self, user_id: str, theme_name: str) -> RecoveryResult:
        """Recover theme from most recent valid backup"""
        
        # Get available backups for this theme
        backups = self.db_manager.execute_query("""
            SELECT backup_id, created_at, checksum 
            FROM theme_backups 
            WHERE user_id = ? AND theme_name = ?
            ORDER BY created_at DESC
            LIMIT 5
        """, (user_id, theme_name))
        
        if not backups:
            return RecoveryResult(
                success=False,
                error="No backups available for recovery",
                recovery_strategy="backup_restore"
            )
        
        # Try each backup until we find a valid one
        for backup in backups:
            try:
                restore_result = self.backup_manager.restore_theme_from_backup(
                    backup['backup_id']
                )
                
                if restore_result.success:
                    # Validate restored data
                    validation_result = self.validator.validate_theme_integrity(
                        restore_result.theme_data
                    )
                    
                    if validation_result.success:
                        return RecoveryResult(
                            success=True,
                            recovered_data=restore_result.theme_data,
                            recovery_strategy="backup_restore",
                            backup_used=backup['backup_id'],
                            data_loss=self._calculate_data_loss(backup['created_at'])
                        )
                
            except Exception as e:
                self.logger.warning(f"Backup {backup['backup_id']} restore failed: {e}")
                continue
        
        return RecoveryResult(
            success=False,
            error="All available backups are corrupted",
            recovery_strategy="backup_restore"
        )
    
    def _sanitize_corrupted_data(self, user_id: str, theme_name: str) -> RecoveryResult:
        """Attempt to sanitize corrupted theme data"""
        
        try:
            # Get corrupted theme data
            corrupted_data = self._get_corrupted_theme_data(user_id, theme_name)
            
            if not corrupted_data:
                return RecoveryResult(
                    success=False,
                    error="Could not retrieve corrupted data",
                    recovery_strategy="data_sanitization"
                )
            
            # Apply sanitization rules
            sanitized_data = self._apply_sanitization_rules(corrupted_data)
            
            # Validate sanitized data
            validation_result = self.validator.validate_theme_integrity(sanitized_data)
            
            if validation_result.success:
                return RecoveryResult(
                    success=True,
                    recovered_data=sanitized_data,
                    recovery_strategy="data_sanitization",
                    data_loss=self._assess_sanitization_data_loss(corrupted_data, sanitized_data)
                )
            else:
                return RecoveryResult(
                    success=False,
                    error="Sanitization failed validation",
                    recovery_strategy="data_sanitization"
                )
                
        except Exception as e:
            return RecoveryResult(
                success=False,
                error=f"Sanitization error: {e}",
                recovery_strategy="data_sanitization"
            )
    
    def _apply_sanitization_rules(self, corrupted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply data sanitization rules to corrupted theme data"""
        
        sanitized = {}
        
        # Sanitize colors
        if 'colors' in corrupted_data:
            sanitized['colors'] = self._sanitize_colors(corrupted_data['colors'])
        
        # Sanitize fonts
        if 'fonts' in corrupted_data:
            sanitized['fonts'] = self._sanitize_fonts(corrupted_data['fonts'])
        
        # Sanitize dimensions
        if 'dimensions' in corrupted_data:
            sanitized['dimensions'] = self._sanitize_dimensions(corrupted_data['dimensions'])
        
        # Add required fields if missing
        sanitized = self._add_required_fields(sanitized)
        
        return sanitized
    
    def _sanitize_colors(self, colors: Any) -> Dict[str, str]:
        """Sanitize color values"""
        import re
        
        if not isinstance(colors, dict):
            return self._get_default_colors()
        
        sanitized_colors = {}
        color_pattern = re.compile(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
        default_colors = self._get_default_colors()
        
        for color_name, color_value in colors.items():
            if isinstance(color_value, str) and color_pattern.match(color_value):
                sanitized_colors[color_name] = color_value
            else:
                # Use default color if available, otherwise use safe fallback
                sanitized_colors[color_name] = default_colors.get(color_name, '#000000')
        
        # Ensure required colors exist
        for required_color in ['primary', 'secondary', 'background', 'text']:
            if required_color not in sanitized_colors:
                sanitized_colors[required_color] = default_colors[required_color]
        
        return sanitized_colors

@dataclass
class RecoveryResult:
    success: bool
    recovered_data: Optional[Dict[str, Any]] = None
    recovery_strategy: Optional[str] = None
    backup_used: Optional[str] = None
    data_loss: bool = False
    error: Optional[str] = None
    recovery_time_ms: Optional[int] = None

enum RecoveryStrategy:
    BACKUP_RESTORE = "backup_restore"
    DATA_SANITIZATION = "data_sanitization"
    FIELD_RECONSTRUCTION = "field_reconstruction"
    TYPE_CORRECTION = "type_correction"
    FULL_BACKUP_RESTORE = "full_backup_restore"
    DEFAULT_FALLBACK = "default_fallback"
```

### 8. Theme Security Integration

#### 8.1 Enhanced Settings Dialog Integration

**File:** `src/rfu/gui/secure_theme_settings.py`

```python
class SecureThemeSettingsWidget(QWidget):
    """
    Enhanced theme settings widget with security features
    and corruption handling capabilities.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_security_manager = ThemeSecurityManager(get_database_manager())
        self.recovery_manager = ThemeRecoveryManager(get_database_manager())
        self.setup_ui()
        self.setup_security_monitoring()
    
    def setup_ui(self):
        """Setup secure theme settings UI"""
        layout = QVBoxLayout(self)
        
        # Theme selection with security indicators
        self.theme_selector = SecureThemeSelector()
        self.theme_selector.theme_selected.connect(self.on_theme_selected)
        layout.addWidget(self.theme_selector)
        
        # Security status indicator
        self.security_status = ThemeSecurityStatusWidget()
        layout.addWidget(self.security_status)
        
        # Theme preview with integrity validation
        self.theme_preview = SecureThemePreview()
        layout.addWidget(self.theme_preview)
        
        # Security controls
        self.security_controls = ThemeSecurityControlsWidget()
        layout.addWidget(self.security_controls)
    
    def on_theme_selected(self, theme_name: str):
        """Handle secure theme selection"""
        try:
            # Validate theme integrity before loading
            validation_result = self.theme_security_manager.validate_theme_integrity(
                self.get_current_user_id(), theme_name
            )
            
            if not validation_result.success:
                self.handle_corrupted_theme(theme_name, validation_result)
                return
            
            # Load theme securely
            retrieval_result = self.theme_security_manager.retrieve_theme_securely(
                self.get_current_user_id(), theme_name
            )
            
            if retrieval_result.success:
                self.apply_theme_safely(retrieval_result.theme_data)
                self.security_status.update_status("secure", "Theme loaded successfully")
            else:
                self.security_status.update_status("error", retrieval_result.error)
                
        except Exception as e:
            self.logger.error(f"Theme selection error: {e}")
            self.security_status.update_status("error", "Theme loading failed")
    
    def handle_corrupted_theme(self, theme_name: str, validation_result: ValidationResult):
        """Handle corrupted theme with user interaction"""
        
        corruption_dialog = ThemeCorruptionDialog(
            theme_name, validation_result.corruption_type, self
        )
        
        if corruption_dialog.exec_() == QDialog.Accepted:
            recovery_option = corruption_dialog.get_selected_recovery_option()
            
            if recovery_option == "auto_recover":
                self.attempt_automatic_recovery(theme_name, validation_result.corruption_type)
            elif recovery_option == "restore_backup":
                self.show_backup_selection_dialog(theme_name)
            elif recovery_option == "reset_default":
                self.reset_to_default_theme(theme_name)
    
    def attempt_automatic_recovery(self, theme_name: str, corruption_type: CorruptionType):
        """Attempt automatic theme recovery"""
        
        progress_dialog = QProgressDialog("Recovering theme...", "Cancel", 0, 0, self)
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.show()
        
        try:
            recovery_result = self.recovery_manager.recover_corrupted_theme(
                self.get_current_user_id(), theme_name, corruption_type
            )
            
            progress_dialog.close()
            
            if recovery_result.success:
                QMessageBox.information(
                    self, "Recovery Successful",
                    f"Theme '{theme_name}' has been successfully recovered.\n"
                    f"Recovery method: {recovery_result.recovery_strategy}\n"
                    f"Data loss: {'Yes' if recovery_result.data_loss else 'No'}"
                )
                self.refresh_theme_list()
            else:
                QMessageBox.warning(
                    self, "Recovery Failed",
                    f"Failed to recover theme '{theme_name}'.\n"
                    f"Error: {recovery_result.error}\n\n"
                    "Please try restoring from backup or resetting to default."
                )
                
        except Exception as e:
            progress_dialog.close()
            QMessageBox.critical(
                self, "Recovery Error",
                f"An error occurred during theme recovery: {e}"
            )

class ThemeCorruptionDialog(QDialog):
    """Dialog for handling theme corruption scenarios"""
    
    def __init__(self, theme_name: str, corruption_type: CorruptionType, parent=None):
        super().__init__(parent)
        self.theme_name = theme_name
        self.corruption_type = corruption_type
        self.setup_ui()
    
    def setup_ui(self):
        """Setup corruption handling dialog UI"""
        self.setWindowTitle("Theme Corruption Detected")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Corruption information
        info_label = QLabel(
            f"Corruption detected in theme '{self.theme_name}'.\n"
            f"Corruption type: {self.corruption_type.value}\n\n"
            "Please select a recovery option:"
        )
        layout.addWidget(info_label)
        
        # Recovery options
        self.recovery_group = QButtonGroup()
        
        self.auto_recover_radio = QRadioButton("Attempt automatic recovery")
        self.auto_recover_radio.setChecked(True)
        self.recovery_group.addButton(self.auto_recover_radio)
        layout.addWidget(self.auto_recover_radio)
        
        self.restore_backup_radio = QRadioButton("Restore from backup")
        self.recovery_group.addButton(self.restore_backup_radio)
        layout.addWidget(self.restore_backup_radio)
        
        self.reset_default_radio = QRadioButton("Reset to default theme")
        self.recovery_group.addButton(self.reset_default_radio)
        layout.addWidget(self.reset_default_radio)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def get_selected_recovery_option(self) -> str:
        """Get selected recovery option"""
        if self.auto_recover_radio.isChecked():
            return "auto_recover"
        elif self.restore_backup_radio.isChecked():
            return "restore_backup"
        elif self.reset_default_radio.isChecked():
            return "reset_default"
        return "auto_recover"
```

### 9. Performance Optimization

#### 9.1 Caching and Performance

```python
class ThemeSecurityCache:
    """
    Caches decrypted theme data and validation results
    with automatic invalidation and security controls.
    """
    
    def __init__(self, max_cache_size: int = 50, cache_ttl: int = 3600):
        self.cache = {}
        self.cache_metadata = {}
        self.max_cache_size = max_cache_size
        self.cache_ttl = cache_ttl
        self.access_times = {}
        self.lock = threading.RLock()
    
    def get_cached_theme(self, user_id: str, theme_name: str) -> Optional[Dict[str, Any]]:
        """Get cached theme data if valid"""
        with self.lock:
            cache_key = f"{user_id}:{theme_name}"
            
            if cache_key not in self.cache:
                return None
            
            # Check TTL
            metadata = self.cache_metadata[cache_key]
            if time.time() - metadata['cached_at'] > self.cache_ttl:
                self._remove_from_cache(cache_key)
                return None
            
            # Update access time
            self.access_times[cache_key] = time.time()
            
            return self.cache[cache_key].copy()
    
    def cache_theme(self, user_id: str, theme_name: str, theme_data: Dict[str, Any]):
        """Cache theme data with metadata"""
        with self.lock:
            cache_key = f"{user_id}:{theme_name}"
            
            # Ensure cache size limit
            if len(self.cache) >= self.max_cache_size:
                self._evict_oldest_entry()
            
            # Cache the data
            self.cache[cache_key] = theme_data.copy()
            self.cache_metadata[cache_key] = {
                'cached_at': time.time(),
                'size_bytes': len(json.dumps(theme_data)),
                'access_count': 1
            }
            self.access_times[cache_key] = time.time()
    
    def invalidate_theme(self, user_id: str, theme_name: str):
        """Invalidate cached theme data"""
        with self.lock:
            cache_key = f"{user_id}:{theme_name}"
            self._remove_from_cache(cache_key)
    
    def _evict_oldest_entry(self):
        """Evict least recently used cache entry"""
        if not self.access_times:
            return
        
        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        self._remove_from_cache(oldest_key)
```

### 10. Testing Strategy

#### 10.1 Security Testing Framework

```python
class ThemeSecurityTestSuite:
    """Comprehensive test suite for theme security features"""
    
    def test_encryption_decryption_cycle(self):
        """Test complete encryption/decryption cycle"""
        
    def test_corruption_detection(self):
        """Test various corruption detection scenarios"""
        
    def test_recovery_mechanisms(self):
        """Test all recovery strategies"""
        
    def test_access_control(self):
        """Test access control and authorization"""
        
    def test_audit_logging(self):
        """Test comprehensive audit logging"""
        
    def test_performance_under_load(self):
        """Test performance with multiple concurrent operations"""
        
    def test_backup_restore_integrity(self):
        """Test backup and restore functionality"""
        
    def test_key_rotation(self):
        """Test encryption key rotation"""
```

## Implementation Checklist

### Core Security Framework
- [ ] Implement `ThemeSecurityManager`
- [ ] Create `ThemeDataEncryption` with AES-256-GCM
- [ ] Build `SecureKeyManager` with OS keyring integration
- [ ] Develop `ThemeIntegrityValidator`
- [ ] Create `ThemeAccessController`

### Corruption Handling
- [ ] Implement `ThemeRecoveryManager`
- [ ] Create corruption detection algorithms
- [ ] Build automatic recovery strategies
- [ ] Develop data sanitization rules
- [ ] Create backup/restore system

### Database Integration
- [ ] Create secure theme storage tables
- [ ] Implement audit logging tables
- [ ] Add permission management tables
- [ ] Create backup tracking tables
- [ ] Add corruption incident logging

### UI Integration
- [ ] Enhance settings dialog with security features
- [ ] Create corruption handling dialogs
- [ ] Add security status indicators
- [ ] Implement secure theme preview
- [ ] Create backup management interface

### Performance & Testing
- [ ] Implement caching system
- [ ] Create performance monitoring
- [ ] Build comprehensive test suite
- [ ] Add security penetration tests
- [ ] Create load testing scenarios

This comprehensive specification ensures robust theme data protection with multiple layers of security, corruption detection, and recovery mechanisms while maintaining excellent user experience and system performance.