-- Migration 004: Secure Directory Storage Schema
-- Creates tables for encrypted directory storage, permissions, audit logging, and PII tracking
-- Author: RFU Development Team
-- Date: 2024
-- Version: 1.0.0

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Begin transaction
BEGIN TRANSACTION;

-- ================================================================
-- SECURE DIRECTORIES TABLE
-- Stores encrypted directory preferences with PII protection
-- ================================================================

CREATE TABLE IF NOT EXISTS secure_directories (
    storage_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    directory_type TEXT NOT NULL CHECK (directory_type IN ('favorite', 'recent', 'default', 'custom')),
    encrypted_path BLOB NOT NULL,
    path_hash TEXT NOT NULL,
    is_pii_sensitive BOOLEAN NOT NULL DEFAULT 0,
    sensitivity_level INTEGER NOT NULL DEFAULT 1 CHECK (sensitivity_level BETWEEN 1 AND 5),
    encryption_metadata TEXT, -- JSON string with encryption details
    pii_indicators TEXT, -- JSON array of PII indicators found
    metadata TEXT, -- JSON string with additional metadata
    created_at TEXT NOT NULL,
    last_accessed_at TEXT NOT NULL,
    access_count INTEGER DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    
    -- Constraints
    UNIQUE(user_id, path_hash),
    CHECK(length(storage_id) > 0),
    CHECK(length(user_id) > 0),
    CHECK(length(tool_name) > 0),
    CHECK(length(path_hash) > 0)
);

-- Indexes for secure_directories
CREATE INDEX IF NOT EXISTS idx_secure_directories_user_id ON secure_directories(user_id);
CREATE INDEX IF NOT EXISTS idx_secure_directories_path_hash ON secure_directories(path_hash);
CREATE INDEX IF NOT EXISTS idx_secure_directories_tool_name ON secure_directories(tool_name);
CREATE INDEX IF NOT EXISTS idx_secure_directories_directory_type ON secure_directories(directory_type);
CREATE INDEX IF NOT EXISTS idx_secure_directories_sensitivity ON secure_directories(sensitivity_level);
CREATE INDEX IF NOT EXISTS idx_secure_directories_pii_sensitive ON secure_directories(is_pii_sensitive);
CREATE INDEX IF NOT EXISTS idx_secure_directories_last_accessed ON secure_directories(last_accessed_at);
CREATE INDEX IF NOT EXISTS idx_secure_directories_active ON secure_directories(is_active);

-- ================================================================
-- DIRECTORY USER ROLES TABLE
-- Manages user roles for directory access control
-- ================================================================

CREATE TABLE IF NOT EXISTS directory_user_roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('guest', 'user', 'power_user', 'admin', 'system')),
    assigned_by TEXT NOT NULL,
    assigned_at TEXT NOT NULL,
    active BOOLEAN NOT NULL DEFAULT 1,
    
    -- Constraints
    CHECK(length(user_id) > 0),
    CHECK(length(assigned_by) > 0)
);

-- Indexes for directory_user_roles
CREATE INDEX IF NOT EXISTS idx_directory_user_roles_user_id ON directory_user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_directory_user_roles_role ON directory_user_roles(role);
CREATE INDEX IF NOT EXISTS idx_directory_user_roles_active ON directory_user_roles(active);
CREATE UNIQUE INDEX IF NOT EXISTS idx_directory_user_roles_active_user ON directory_user_roles(user_id) WHERE active = 1;

-- ================================================================
-- DIRECTORY PERMISSIONS TABLE
-- Manages explicit directory permissions and access control
-- ================================================================

CREATE TABLE IF NOT EXISTS directory_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    resource_path TEXT NOT NULL, -- Can be specific path hash or '*' for global
    permission_level INTEGER NOT NULL CHECK (permission_level BETWEEN 0 AND 4),
    role TEXT NOT NULL CHECK (role IN ('guest', 'user', 'power_user', 'admin', 'system')),
    granted_by TEXT NOT NULL,
    granted_at TEXT NOT NULL,
    expires_at TEXT, -- NULL for never expires
    restrictions TEXT, -- JSON string with permission restrictions
    active BOOLEAN NOT NULL DEFAULT 1,
    revoked_at TEXT,
    revoked_by TEXT,
    
    -- Constraints
    CHECK(length(user_id) > 0),
    CHECK(length(resource_path) > 0),
    CHECK(length(granted_by) > 0)
);

-- Indexes for directory_permissions
CREATE INDEX IF NOT EXISTS idx_directory_permissions_user_id ON directory_permissions(user_id);
CREATE INDEX IF NOT EXISTS idx_directory_permissions_resource ON directory_permissions(resource_path);
CREATE INDEX IF NOT EXISTS idx_directory_permissions_level ON directory_permissions(permission_level);
CREATE INDEX IF NOT EXISTS idx_directory_permissions_granted_by ON directory_permissions(granted_by);
CREATE INDEX IF NOT EXISTS idx_directory_permissions_expires ON directory_permissions(expires_at);
CREATE INDEX IF NOT EXISTS idx_directory_permissions_active ON directory_permissions(active);
CREATE UNIQUE INDEX IF NOT EXISTS idx_directory_permissions_unique ON directory_permissions(user_id, resource_path) WHERE active = 1;

-- ================================================================
-- DIRECTORY AUDIT LOG TABLE
-- Comprehensive audit logging for directory operations
-- ================================================================

CREATE TABLE IF NOT EXISTS directory_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL UNIQUE,
    event_type TEXT NOT NULL CHECK (event_type IN (
        'directory_access', 'directory_store', 'directory_retrieve', 'directory_delete',
        'directory_list', 'permission_grant', 'permission_revoke', 'role_assignment',
        'security_violation', 'access_denied', 'encryption_event', 'pii_detection',
        'system_event'
    )),
    severity TEXT NOT NULL CHECK (severity IN ('info', 'warning', 'error', 'critical')),
    user_id TEXT NOT NULL,
    resource_id TEXT, -- Path hash or resource identifier
    action TEXT NOT NULL,
    success BOOLEAN NOT NULL,
    details TEXT NOT NULL, -- JSON string with event details
    timestamp TEXT NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    session_id TEXT,
    anonymized_data TEXT, -- JSON string with anonymized data for reporting
    
    -- Constraints
    CHECK(length(event_id) > 0),
    CHECK(length(user_id) > 0),
    CHECK(length(action) > 0),
    CHECK(length(details) > 0)
);

-- Indexes for directory_audit_log
CREATE INDEX IF NOT EXISTS idx_directory_audit_event_id ON directory_audit_log(event_id);
CREATE INDEX IF NOT EXISTS idx_directory_audit_user_id ON directory_audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_directory_audit_event_type ON directory_audit_log(event_type);
CREATE INDEX IF NOT EXISTS idx_directory_audit_severity ON directory_audit_log(severity);
CREATE INDEX IF NOT EXISTS idx_directory_audit_timestamp ON directory_audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_directory_audit_success ON directory_audit_log(success);
CREATE INDEX IF NOT EXISTS idx_directory_audit_resource ON directory_audit_log(resource_id);
CREATE INDEX IF NOT EXISTS idx_directory_audit_action ON directory_audit_log(action);

-- ================================================================
-- PII DETECTION INCIDENTS TABLE
-- Tracks PII detection incidents for compliance reporting
-- ================================================================

CREATE TABLE IF NOT EXISTS pii_detection_incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id TEXT NOT NULL UNIQUE,
    user_id TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    pii_indicators TEXT NOT NULL, -- JSON array of detected PII types
    sensitivity_level INTEGER NOT NULL CHECK (sensitivity_level BETWEEN 1 AND 5),
    anonymized_path TEXT NOT NULL,
    detection_timestamp TEXT NOT NULL,
    handled BOOLEAN NOT NULL DEFAULT 0,
    handled_by TEXT,
    handled_at TEXT,
    resolution_notes TEXT,
    
    -- Constraints
    CHECK(length(incident_id) > 0),
    CHECK(length(user_id) > 0),
    CHECK(length(resource_id) > 0),
    CHECK(length(pii_indicators) > 0),
    CHECK(length(anonymized_path) > 0)
);

-- Indexes for pii_detection_incidents
CREATE INDEX IF NOT EXISTS idx_pii_incidents_user_id ON pii_detection_incidents(user_id);
CREATE INDEX IF NOT EXISTS idx_pii_incidents_resource ON pii_detection_incidents(resource_id);
CREATE INDEX IF NOT EXISTS idx_pii_incidents_sensitivity ON pii_detection_incidents(sensitivity_level);
CREATE INDEX IF NOT EXISTS idx_pii_incidents_timestamp ON pii_detection_incidents(detection_timestamp);
CREATE INDEX IF NOT EXISTS idx_pii_incidents_handled ON pii_detection_incidents(handled);
CREATE INDEX IF NOT EXISTS idx_pii_incidents_incident_id ON pii_detection_incidents(incident_id);

-- ================================================================
-- SECURITY INCIDENTS TABLE
-- Tracks security violations and incidents
-- ================================================================

CREATE TABLE IF NOT EXISTS security_incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id TEXT NOT NULL UNIQUE,
    incident_type TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    user_id TEXT NOT NULL,
    resource_id TEXT,
    description TEXT NOT NULL,
    details TEXT, -- JSON string with incident details
    detected_at TEXT NOT NULL,
    resolved BOOLEAN NOT NULL DEFAULT 0,
    resolved_by TEXT,
    resolved_at TEXT,
    resolution_notes TEXT,
    false_positive BOOLEAN NOT NULL DEFAULT 0,
    
    -- Constraints
    CHECK(length(incident_id) > 0),
    CHECK(length(incident_type) > 0),
    CHECK(length(user_id) > 0),
    CHECK(length(description) > 0)
);

-- Indexes for security_incidents
CREATE INDEX IF NOT EXISTS idx_security_incidents_user_id ON security_incidents(user_id);
CREATE INDEX IF NOT EXISTS idx_security_incidents_type ON security_incidents(incident_type);
CREATE INDEX IF NOT EXISTS idx_security_incidents_severity ON security_incidents(severity);
CREATE INDEX IF NOT EXISTS idx_security_incidents_detected ON security_incidents(detected_at);
CREATE INDEX IF NOT EXISTS idx_security_incidents_resolved ON security_incidents(resolved);
CREATE INDEX IF NOT EXISTS idx_security_incidents_incident_id ON security_incidents(incident_id);

-- ================================================================
-- DIRECTORY ACCESS STATISTICS TABLE
-- Tracks access patterns for analytics and monitoring
-- ================================================================

CREATE TABLE IF NOT EXISTS directory_access_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    directory_type TEXT NOT NULL,
    access_date TEXT NOT NULL, -- Date only (YYYY-MM-DD)
    access_count INTEGER NOT NULL DEFAULT 1,
    unique_paths INTEGER NOT NULL DEFAULT 1,
    pii_accesses INTEGER NOT NULL DEFAULT 0,
    high_sensitivity_accesses INTEGER NOT NULL DEFAULT 0,
    
    -- Constraints
    CHECK(length(user_id) > 0),
    CHECK(length(tool_name) > 0),
    CHECK(length(directory_type) > 0),
    CHECK(access_count >= 0),
    CHECK(unique_paths >= 0),
    CHECK(pii_accesses >= 0),
    CHECK(high_sensitivity_accesses >= 0)
);

-- Indexes for directory_access_stats
CREATE INDEX IF NOT EXISTS idx_directory_stats_user_id ON directory_access_stats(user_id);
CREATE INDEX IF NOT EXISTS idx_directory_stats_tool ON directory_access_stats(tool_name);
CREATE INDEX IF NOT EXISTS idx_directory_stats_type ON directory_access_stats(directory_type);
CREATE INDEX IF NOT EXISTS idx_directory_stats_date ON directory_access_stats(access_date);
CREATE UNIQUE INDEX IF NOT EXISTS idx_directory_stats_unique ON directory_access_stats(user_id, tool_name, directory_type, access_date);

-- ================================================================
-- ENCRYPTION KEY METADATA TABLE
-- Tracks encryption key information (not the keys themselves)
-- ================================================================

CREATE TABLE IF NOT EXISTS encryption_key_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_id TEXT NOT NULL UNIQUE,
    algorithm TEXT NOT NULL,
    key_length INTEGER NOT NULL,
    kdf_algorithm TEXT NOT NULL,
    kdf_iterations INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    rotated_at TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'rotated', 'revoked')),
    version INTEGER NOT NULL DEFAULT 1,
    
    -- Constraints
    CHECK(length(key_id) > 0),
    CHECK(length(algorithm) > 0),
    CHECK(length(kdf_algorithm) > 0),
    CHECK(key_length > 0),
    CHECK(kdf_iterations > 0),
    CHECK(version > 0)
);

-- Indexes for encryption_key_metadata
CREATE INDEX IF NOT EXISTS idx_encryption_keys_key_id ON encryption_key_metadata(key_id);
CREATE INDEX IF NOT EXISTS idx_encryption_keys_status ON encryption_key_metadata(status);
CREATE INDEX IF NOT EXISTS idx_encryption_keys_version ON encryption_key_metadata(version);
CREATE INDEX IF NOT EXISTS idx_encryption_keys_created ON encryption_key_metadata(created_at);

-- ================================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- ================================================================

-- Trigger to update access count and last accessed time
CREATE TRIGGER IF NOT EXISTS update_directory_access_stats
AFTER UPDATE OF last_accessed_at ON secure_directories
FOR EACH ROW
BEGIN
    UPDATE secure_directories 
    SET access_count = access_count + 1 
    WHERE storage_id = NEW.storage_id;
    
    INSERT OR REPLACE INTO directory_access_stats 
    (user_id, tool_name, directory_type, access_date, access_count, unique_paths, 
     pii_accesses, high_sensitivity_accesses)
    VALUES (
        NEW.user_id, 
        NEW.tool_name, 
        NEW.directory_type, 
        date(NEW.last_accessed_at),
        COALESCE((SELECT access_count FROM directory_access_stats 
                 WHERE user_id = NEW.user_id AND tool_name = NEW.tool_name 
                 AND directory_type = NEW.directory_type AND access_date = date(NEW.last_accessed_at)), 0) + 1,
        COALESCE((SELECT unique_paths FROM directory_access_stats 
                 WHERE user_id = NEW.user_id AND tool_name = NEW.tool_name 
                 AND directory_type = NEW.directory_type AND access_date = date(NEW.last_accessed_at)), 1),
        COALESCE((SELECT pii_accesses FROM directory_access_stats 
                 WHERE user_id = NEW.user_id AND tool_name = NEW.tool_name 
                 AND directory_type = NEW.directory_type AND access_date = date(NEW.last_accessed_at)), 0) + 
                 CASE WHEN NEW.is_pii_sensitive = 1 THEN 1 ELSE 0 END,
        COALESCE((SELECT high_sensitivity_accesses FROM directory_access_stats 
                 WHERE user_id = NEW.user_id AND tool_name = NEW.tool_name 
                 AND directory_type = NEW.directory_type AND access_date = date(NEW.last_accessed_at)), 0) + 
                 CASE WHEN NEW.sensitivity_level >= 4 THEN 1 ELSE 0 END
    );
END;

-- Trigger to create PII detection incidents for high sensitivity paths
CREATE TRIGGER IF NOT EXISTS create_pii_incident
AFTER INSERT ON secure_directories
FOR EACH ROW
WHEN NEW.is_pii_sensitive = 1 AND NEW.sensitivity_level >= 4
BEGIN
    INSERT INTO pii_detection_incidents 
    (incident_id, user_id, resource_id, pii_indicators, sensitivity_level, 
     anonymized_path, detection_timestamp)
    VALUES (
        'pii_' || datetime('now') || '_' || substr(NEW.storage_id, 1, 8),
        NEW.user_id,
        NEW.path_hash,
        NEW.pii_indicators,
        NEW.sensitivity_level,
        '[REDACTED_PATH_' || substr(NEW.path_hash, 1, 8) || ']',
        datetime('now')
    );
END;

-- ================================================================
-- VIEWS FOR SECURITY MONITORING
-- ================================================================

-- View for security monitoring dashboard
CREATE VIEW IF NOT EXISTS security_monitoring_view AS
SELECT 
    'directory_access' as metric_type,
    COUNT(*) as count,
    date(last_accessed_at) as date,
    'daily' as period
FROM secure_directories 
WHERE date(last_accessed_at) >= date('now', '-7 days')
GROUP BY date(last_accessed_at)

UNION ALL

SELECT 
    'pii_incidents' as metric_type,
    COUNT(*) as count,
    date(detection_timestamp) as date,
    'daily' as period
FROM pii_detection_incidents 
WHERE date(detection_timestamp) >= date('now', '-7 days')
GROUP BY date(detection_timestamp)

UNION ALL

SELECT 
    'security_violations' as metric_type,
    COUNT(*) as count,
    date(timestamp) as date,
    'daily' as period
FROM directory_audit_log 
WHERE event_type = 'security_violation' 
AND date(timestamp) >= date('now', '-7 days')
GROUP BY date(timestamp);

-- View for compliance reporting
CREATE VIEW IF NOT EXISTS compliance_reporting_view AS
SELECT 
    u.user_id,
    COUNT(DISTINCT d.storage_id) as total_directories,
    COUNT(DISTINCT CASE WHEN d.is_pii_sensitive = 1 THEN d.storage_id END) as pii_directories,
    MAX(d.sensitivity_level) as max_sensitivity_level,
    COUNT(DISTINCT p.id) as permission_grants,
    COUNT(DISTINCT CASE WHEN a.event_type = 'security_violation' THEN a.id END) as security_violations
FROM directory_user_roles u
LEFT JOIN secure_directories d ON u.user_id = d.user_id
LEFT JOIN directory_permissions p ON u.user_id = p.user_id
LEFT JOIN directory_audit_log a ON u.user_id = a.user_id
WHERE u.active = 1
GROUP BY u.user_id;

-- ================================================================
-- INSERT DEFAULT DATA
-- ================================================================

-- Insert default encryption key metadata
INSERT OR IGNORE INTO encryption_key_metadata 
(key_id, algorithm, key_length, kdf_algorithm, kdf_iterations, created_at, version)
VALUES 
('default_aes_256_gcm_v1', 'AES-256-GCM', 256, 'PBKDF2-SHA256', 100000, datetime('now'), 1);

-- Insert system admin role (if not exists)
INSERT OR IGNORE INTO directory_user_roles 
(user_id, role, assigned_by, assigned_at, active)
VALUES 
('system', 'system', 'system', datetime('now'), 1);

-- ================================================================
-- COMMIT TRANSACTION
-- ================================================================

-- Update schema version
INSERT OR REPLACE INTO rfu_schema_version (version, applied_at, description) 
VALUES (4, datetime('now'), 'Secure Directory Storage Schema with PII Protection');

COMMIT;

-- ================================================================
-- MIGRATION VERIFICATION
-- ================================================================

-- Verify all tables were created
SELECT 
    'Tables created: ' || COUNT(*) as result
FROM sqlite_master 
WHERE type = 'table' 
AND name IN (
    'secure_directories', 'directory_user_roles', 'directory_permissions',
    'directory_audit_log', 'pii_detection_incidents', 'security_incidents',
    'directory_access_stats', 'encryption_key_metadata'
);

-- Verify all indexes were created
SELECT 
    'Indexes created: ' || COUNT(*) as result
FROM sqlite_master 
WHERE type = 'index' 
AND name LIKE 'idx_%directory%';

-- Verify triggers were created
SELECT 
    'Triggers created: ' || COUNT(*) as result
FROM sqlite_master 
WHERE type = 'trigger' 
AND name IN ('update_directory_access_stats', 'create_pii_incident');

-- Verify views were created
SELECT 
    'Views created: ' || COUNT(*) as result
FROM sqlite_master 
WHERE type = 'view' 
AND name IN ('security_monitoring_view', 'compliance_reporting_view');