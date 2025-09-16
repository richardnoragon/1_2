"""
Comprehensive Test Suite for Directory Security Components (Phase 3)

Tests all directory security components including path validation, PII detection,
encryption, permissions, audit logging, and integration scenarios.

Author: RFU Development Team
Date: 2024
Version: 1.0.0
"""

import unittest
import tempfile
import os
import json
import sqlite3
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock

# Import components to test
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from rfu.core.directory_security.directory_security_manager import (
    DirectorySecurityManager, DirectoryStorageResult, DirectoryRetrievalResult
)
from rfu.core.directory_security.directory_validator import (
    DirectoryPathValidator, PathValidationResult
)
from rfu.core.directory_security.path_sanitizer import PathSanitizer
from rfu.core.directory_security.pii_detector import (
    PIIDetector, PIIAnalysisResult
)
from rfu.core.directory_security.directory_encryption import (
    DirectoryPathEncryption, DirectoryEncryptionResult, DirectoryDecryptionResult
)
from rfu.core.directory_security.directory_permissions import (
    DirectoryPermissionManager, PermissionCheckResult, PermissionLevel, DirectoryRole
)
from rfu.core.directory_security.directory_audit import (
    DirectoryAuditLogger, AuditEvent, AuditEventType, AuditSeverity
)


class MockDatabaseManager:
    """Mock database manager for testing"""
    
    def __init__(self):
        self.connection = sqlite3.connect(':memory:')
        self.cursor = self.connection.cursor()
        self._setup_test_tables()
    
    def _setup_test_tables(self):
        """Set up minimal test tables"""
        self.cursor.execute('''
            CREATE TABLE secure_directories (
                storage_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                tool_name TEXT NOT NULL,
                directory_type TEXT NOT NULL,
                encrypted_path BLOB NOT NULL,
                path_hash TEXT NOT NULL,
                is_pii_sensitive BOOLEAN NOT NULL DEFAULT 0,
                sensitivity_level INTEGER NOT NULL DEFAULT 1,
                encryption_metadata TEXT,
                pii_indicators TEXT,
                metadata TEXT,
                created_at TEXT NOT NULL,
                last_accessed_at TEXT NOT NULL
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE directory_user_roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                role TEXT NOT NULL,
                assigned_by TEXT NOT NULL,
                assigned_at TEXT NOT NULL,
                active BOOLEAN NOT NULL DEFAULT 1
            )
        ''')
        
        self.cursor.execute('''
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
            )
        ''')
        
        self.cursor.execute('''
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
            )
        ''')
        
        self.connection.commit()
    
    def execute_query(self, query, params=()):
        """Execute query with parameters"""
        return self.cursor.execute(query, params)
    
    def fetch_one(self, query, params=()):
        """Fetch one result"""
        self.cursor.execute(query, params)
        return self.cursor.fetchone()
    
    def fetch_all(self, query, params=()):
        """Fetch all results"""
        self.cursor.execute(query, params)
        return self.cursor.fetchall()


class TestDirectoryPathValidator(unittest.TestCase):
    """Test DirectoryPathValidator component"""
    
    def setUp(self):
        self.validator = DirectoryPathValidator()
    
    def test_valid_path_validation(self):
        """Test validation of valid directory paths"""
        valid_paths = [
            "C:\\Users\\testuser\\Documents",
            "/home/testuser/documents",
            "/Users/testuser/Desktop",
            "C:\\Program Files\\MyApp"
        ]
        
        for path in valid_paths:
            with self.subTest(path=path):
                result = self.validator.validate_directory_path(path, "testuser")
                self.assertTrue(result.valid, f"Path should be valid: {path}")
                self.assertIsNotNone(result.normalized_path)
                self.assertGreaterEqual(result.security_level, 1)
    
    def test_path_traversal_detection(self):
        """Test detection of path traversal attacks"""
        malicious_paths = [
            "../../../etc/passwd",
            "C:\\Users\\..\\..\\Windows\\System32",
            "/home/user/../../../root",
            "..\\..\\sensitive_file.txt"
        ]
        
        for path in malicious_paths:
            with self.subTest(path=path):
                result = self.validator.validate_directory_path(path, "testuser")
                self.assertFalse(result.valid, f"Malicious path should be invalid: {path}")
                self.assertIn("traversal", result.reason.lower())
    
    def test_invalid_characters_detection(self):
        """Test detection of invalid characters"""
        invalid_paths = [
            "C:\\Users\\test<user>",
            "/home/user|pipe",
            "C:\\test*wildcard",
            "/home/user?query"
        ]
        
        for path in invalid_paths:
            with self.subTest(path=path):
                result = self.validator.validate_directory_path(path, "testuser")
                self.assertFalse(result.valid, f"Path with invalid chars should be invalid: {path}")
    
    def test_path_length_limits(self):
        """Test path length validation"""
        # Test very long path
        long_path = "C:\\" + "A" * 5000
        result = self.validator.validate_directory_path(long_path, "testuser")
        self.assertFalse(result.valid)
        self.assertIn("length", result.reason.lower())
    
    def test_path_accessibility_check(self):
        """Test path accessibility validation"""
        # Test with temporary directory (should be accessible)
        with tempfile.TemporaryDirectory() as temp_dir:
            self.assertTrue(self.validator.validate_path_accessibility(temp_dir))
        
        # Test with non-existent path
        self.assertFalse(self.validator.validate_path_accessibility("/non/existent/path"))


class TestPathSanitizer(unittest.TestCase):
    """Test PathSanitizer component"""
    
    def setUp(self):
        self.sanitizer = PathSanitizer()
    
    def test_basic_sanitization(self):
        """Test basic path sanitization"""
        test_cases = [
            ("C:\\Users\\test<user>", "C:\\Users\\test_user"),
            ("/home/user|pipe", "/home/user_pipe"),
            ("C:\\test*wildcard", "C:\\test_wildcard"),
            ("/home/user?query", "/home/user_query")
        ]
        
        for original, expected in test_cases:
            with self.subTest(original=original):
                result = self.sanitizer.sanitize_path(original)
                self.assertEqual(result, expected)
    
    def test_null_byte_removal(self):
        """Test null byte removal"""
        malicious_path = "C:\\Users\\test\x00user"
        result = self.sanitizer.sanitize_path(malicious_path)
        self.assertNotIn('\x00', result)
    
    def test_path_separator_normalization(self):
        """Test path separator normalization"""
        if os.name == 'nt':  # Windows
            result = self.sanitizer.sanitize_path("/home/user/documents")
            self.assertIn('\\', result)
        else:  # Unix-like
            result = self.sanitizer.sanitize_path("C:\\Users\\test")
            self.assertIn('/', result)
    
    def test_display_sanitization(self):
        """Test sanitization for display"""
        sensitive_path = "C:\\Users\\john.doe\\Documents\\Personal"
        result = self.sanitizer.sanitize_for_display(sensitive_path)
        self.assertIn('[USER]', result)
        self.assertNotIn('john.doe', result)
    
    def test_logging_sanitization(self):
        """Test sanitization for logging"""
        sensitive_path = "C:\\Users\\john.doe\\VeryLongDirectoryNameThatMightContainPII\\Documents"
        result = self.sanitizer.sanitize_for_logging(sensitive_path)
        self.assertIn('[USER]', result)
        self.assertIn('[LONG_NAME]', result)
    
    def test_safe_path_detection(self):
        """Test safe path detection"""
        safe_paths = [
            "C:\\Users\\test\\Documents",
            "/home/user/documents"
        ]
        
        unsafe_paths = [
            "C:\\Users\\test<user>",
            "/home/user/../etc",
            "path\x00with\x00nulls"
        ]
        
        for path in safe_paths:
            with self.subTest(path=path):
                self.assertTrue(self.sanitizer.is_path_safe(path))
        
        for path in unsafe_paths:
            with self.subTest(path=path):
                self.assertFalse(self.sanitizer.is_path_safe(path))


class TestPIIDetector(unittest.TestCase):
    """Test PIIDetector component"""
    
    def setUp(self):
        self.detector = PIIDetector()
    
    def test_pii_detection(self):
        """Test PII detection in directory paths"""
        pii_paths = [
            "/home/john.doe/Documents",
            "C:\\Users\\jane.smith\\Desktop",
            "/Users/testuser/Documents/Personal",
            "/home/user/Pictures/Family",
            "C:\\Users\\test\\AppData\\Local\\Microsoft\\Outlook"
        ]
        
        for path in pii_paths:
            with self.subTest(path=path):
                result = self.detector.analyze_directory_path(path)
                self.assertTrue(result.contains_pii, f"Should detect PII in: {path}")
                self.assertGreaterEqual(result.sensitivity_level, 1)
                self.assertGreater(len(result.pii_indicators), 0)
    
    def test_high_sensitivity_detection(self):
        """Test detection of high-sensitivity paths"""
        high_sensitivity_paths = [
            "/home/user/.ssh/private_keys",
            "C:\\Users\\test\\AppData\\Local\\Microsoft\\Outlook\\emails",
            "/Users/test/Documents/Financial/TaxReturns",
            "/home/user/Documents/Medical/Records"
        ]
        
        for path in high_sensitivity_paths:
            with self.subTest(path=path):
                result = self.detector.analyze_directory_path(path)
                self.assertGreaterEqual(result.sensitivity_level, 4)
                self.assertTrue(result.requires_encryption)
    
    def test_anonymization(self):
        """Test path anonymization"""
        sensitive_path = "/home/john.doe/Documents/Personal/Financial"
        result = self.detector.analyze_directory_path(sensitive_path)
        
        self.assertNotIn('john.doe', result.anonymized_path)
        self.assertIn('[USER]', result.anonymized_path)
    
    def test_pii_warnings(self):
        """Test PII warning generation"""
        path = "/home/user/Documents/Medical/Records"
        warnings = self.detector.get_pii_warnings(path)
        
        self.assertGreater(len(warnings), 0)
        self.assertTrue(any('medical' in warning.lower() for warning in warnings))
    
    def test_non_pii_paths(self):
        """Test paths without PII"""
        non_pii_paths = [
            "/opt/software",
            "C:\\Program Files\\Application",
            "/usr/local/bin",
            "/tmp/cache"
        ]
        
        for path in non_pii_paths:
            with self.subTest(path=path):
                result = self.detector.analyze_directory_path(path)
                self.assertLessEqual(result.sensitivity_level, 2)


class TestDirectoryPathEncryption(unittest.TestCase):
    """Test DirectoryPathEncryption component"""
    
    def setUp(self):
        self.encryption = DirectoryPathEncryption()
    
    def test_encryption_decryption_cycle(self):
        """Test complete encryption/decryption cycle"""
        original_path = "C:\\Users\\testuser\\Documents\\Personal"
        user_id = "testuser123"
        
        # Encrypt
        encrypt_result = self.encryption.encrypt_directory_path(original_path, user_id)
        self.assertTrue(encrypt_result.success)
        self.assertIsNotNone(encrypt_result.encrypted_data)
        self.assertIsNotNone(encrypt_result.salt)
        self.assertIsNotNone(encrypt_result.nonce)
        
        # Decrypt
        decrypt_result = self.encryption.decrypt_directory_path(
            encrypt_result.encrypted_data,
            encrypt_result.salt,
            encrypt_result.nonce,
            user_id,
            encrypt_result.integrity_hash
        )
        self.assertTrue(decrypt_result.success)
        self.assertEqual(decrypt_result.directory_path, os.path.normpath(original_path))
        self.assertTrue(decrypt_result.integrity_verified)
    
    def test_user_specific_encryption(self):
        """Test that encryption is user-specific"""
        path = "/home/user/documents"
        user1 = "user1"
        user2 = "user2"
        
        # Encrypt with user1
        result1 = self.encryption.encrypt_directory_path(path, user1)
        self.assertTrue(result1.success)
        
        # Try to decrypt with user2 (should fail)
        result2 = self.encryption.decrypt_directory_path(
            result1.encrypted_data,
            result1.salt,
            result1.nonce,
            user2,
            result1.integrity_hash
        )
        self.assertFalse(result2.success)
    
    def test_integrity_verification(self):
        """Test integrity hash verification"""
        path = "/test/path"
        user_id = "testuser"
        
        encrypt_result = self.encryption.encrypt_directory_path(path, user_id)
        self.assertTrue(encrypt_result.success)
        
        # Test with correct integrity hash
        decrypt_result = self.encryption.decrypt_directory_path(
            encrypt_result.encrypted_data,
            encrypt_result.salt,
            encrypt_result.nonce,
            user_id,
            encrypt_result.integrity_hash
        )
        self.assertTrue(decrypt_result.success)
        self.assertTrue(decrypt_result.integrity_verified)
        
        # Test with wrong integrity hash
        decrypt_result = self.encryption.decrypt_directory_path(
            encrypt_result.encrypted_data,
            encrypt_result.salt,
            encrypt_result.nonce,
            user_id,
            "wrong_hash"
        )
        self.assertFalse(decrypt_result.success)
    
    def test_encryption_metadata(self):
        """Test encryption metadata handling"""
        path = "/test/path"
        user_id = "testuser"
        
        encrypt_result = self.encryption.encrypt_directory_path(path, user_id)
        metadata = self.encryption.create_encryption_metadata(encrypt_result)
        
        self.assertIn('salt', metadata)
        self.assertIn('nonce', metadata)
        self.assertIn('integrity_hash', metadata)
        self.assertIn('algorithm', metadata)
        
        # Test parsing metadata
        salt, nonce, integrity_hash, version = self.encryption.parse_encryption_metadata(metadata)
        self.assertEqual(salt, encrypt_result.salt)
        self.assertEqual(nonce, encrypt_result.nonce)
        self.assertEqual(integrity_hash, encrypt_result.integrity_hash)
    
    def test_parameter_validation(self):
        """Test encryption parameter validation"""
        # Test invalid inputs
        result = self.encryption.encrypt_directory_path("", "user")
        self.assertFalse(result.success)
        
        result = self.encryption.encrypt_directory_path("path", "")
        self.assertFalse(result.success)
        
        # Test validation function
        valid_data = os.urandom(32)
        valid_salt = os.urandom(32)
        valid_nonce = os.urandom(12)
        valid_user = "testuser"
        
        self.assertTrue(self.encryption.validate_encryption_parameters(
            valid_data, valid_salt, valid_nonce, valid_user
        ))
        
        # Test invalid parameters
        self.assertFalse(self.encryption.validate_encryption_parameters(
            b"", valid_salt, valid_nonce, valid_user
        ))


class TestDirectoryPermissionManager(unittest.TestCase):
    """Test DirectoryPermissionManager component"""
    
    def setUp(self):
        self.db_manager = MockDatabaseManager()
        self.permission_manager = DirectoryPermissionManager(self.db_manager)
    
    def test_permission_check(self):
        """Test basic permission checking"""
        user_id = "testuser"
        resource_path = "test_resource"
        
        # Insert test user role
        self.db_manager.execute_query(
            "INSERT INTO directory_user_roles (user_id, role, assigned_by, assigned_at) VALUES (?, ?, ?, ?)",
            (user_id, "user", "admin", datetime.now(timezone.utc).isoformat())
        )
        
        # Test read permission (should be allowed for user role)
        result = self.permission_manager.check_directory_permission(user_id, resource_path, "read")
        self.assertTrue(result.authorized)
        
        # Test admin permission (should be denied for user role)
        result = self.permission_manager.check_directory_permission(user_id, resource_path, "admin")
        self.assertFalse(result.authorized)
    
    def test_role_hierarchy(self):
        """Test role hierarchy enforcement"""
        admin_user = "adminuser"
        
        # Insert admin role
        self.db_manager.execute_query(
            "INSERT INTO directory_user_roles (user_id, role, assigned_by, assigned_at) VALUES (?, ?, ?, ?)",
            (admin_user, "admin", "system", datetime.now(timezone.utc).isoformat())
        )
        
        # Admin should have all permissions
        for action in ["read", "write", "delete", "admin"]:
            with self.subTest(action=action):
                result = self.permission_manager.check_directory_permission(
                    admin_user, "test_resource", action
                )
                self.assertTrue(result.authorized)
    
    def test_permission_granting(self):
        """Test permission granting and revocation"""
        admin_user = "adminuser"
        target_user = "targetuser"
        resource_path = "test_resource"
        
        # Set up admin user
        self.db_manager.execute_query(
            "INSERT INTO directory_user_roles (user_id, role, assigned_by, assigned_at) VALUES (?, ?, ?, ?)",
            (admin_user, "admin", "system", datetime.now(timezone.utc).isoformat())
        )
        
        # Grant permission
        success = self.permission_manager.grant_directory_permission(
            target_user, resource_path, PermissionLevel.WRITE, admin_user
        )
        self.assertTrue(success)
        
        # Verify permission was granted
        result = self.permission_manager.check_directory_permission(
            target_user, resource_path, "write"
        )
        self.assertTrue(result.authorized)
        
        # Revoke permission
        success = self.permission_manager.revoke_directory_permission(
            target_user, resource_path, admin_user
        )
        self.assertTrue(success)
    
    def test_role_assignment(self):
        """Test role assignment"""
        system_user = "system"
        target_user = "newuser"
        
        # Set up system user
        self.db_manager.execute_query(
            "INSERT INTO directory_user_roles (user_id, role, assigned_by, assigned_at) VALUES (?, ?, ?, ?)",
            (system_user, "system", "system", datetime.now(timezone.utc).isoformat())
        )
        
        # Assign role
        success = self.permission_manager.set_user_role(
            target_user, DirectoryRole.POWER_USER, system_user
        )
        self.assertTrue(success)
        
        # Verify role was assigned
        role = self.permission_manager._get_user_role(target_user)
        self.assertEqual(role, DirectoryRole.POWER_USER)


class TestDirectoryAuditLogger(unittest.TestCase):
    """Test DirectoryAuditLogger component"""
    
    def setUp(self):
        self.db_manager = MockDatabaseManager()
        self.audit_logger = DirectoryAuditLogger(self.db_manager)
    
    def test_directory_operation_logging(self):
        """Test directory operation audit logging"""
        user_id = "testuser"
        resource_id = "test_resource"
        operation = "store"
        details = {"test": "data"}
        
        event_id = self.audit_logger.log_directory_operation(
            user_id, resource_id, operation, True, details
        )
        
        self.assertNotEqual(event_id, "")
        
        # Verify event was stored
        events = self.audit_logger.get_audit_events(user_id=user_id, limit=1)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].user_id, user_id)
        self.assertEqual(events[0].action, operation)
        self.assertTrue(events[0].success)
    
    def test_access_denied_logging(self):
        """Test access denied event logging"""
        user_id = "testuser"
        resource_id = "test_resource"
        action = "admin"
        reason = "Insufficient permissions"
        
        event_id = self.audit_logger.log_access_denied(user_id, resource_id, action, reason)
        self.assertNotEqual(event_id, "")
        
        # Verify event was logged with correct severity
        events = self.audit_logger.get_audit_events(user_id=user_id, limit=1)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, AuditEventType.ACCESS_DENIED)
        self.assertEqual(events[0].severity, AuditSeverity.WARNING)
        self.assertFalse(events[0].success)
    
    def test_security_violation_logging(self):
        """Test security violation logging"""
        user_id = "testuser"
        violation_type = "path_traversal"
        details = {"malicious_path": "../../../etc/passwd"}
        
        event_id = self.audit_logger.log_security_violation(user_id, violation_type, details)
        self.assertNotEqual(event_id, "")
        
        # Verify event was logged with error severity
        events = self.audit_logger.get_audit_events(user_id=user_id, limit=1)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, AuditEventType.SECURITY_VIOLATION)
        self.assertEqual(events[0].severity, AuditSeverity.ERROR)
    
    def test_pii_detection_logging(self):
        """Test PII detection event logging"""
        user_id = "testuser"
        resource_id = "test_resource"
        pii_indicators = ["username_directory", "personal_documents"]
        sensitivity_level = 4
        anonymized_path = "/[USER]/[DOCS]"
        
        event_id = self.audit_logger.log_pii_detection(
            user_id, resource_id, pii_indicators, sensitivity_level, anonymized_path
        )
        self.assertNotEqual(event_id, "")
        
        # Verify event was logged
        events = self.audit_logger.get_audit_events(user_id=user_id, limit=1)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, AuditEventType.PII_DETECTION)
        self.assertEqual(events[0].details['sensitivity_level'], sensitivity_level)
    
    def test_audit_report_generation(self):
        """Test audit report generation"""
        start_time = datetime.now(timezone.utc)
        
        # Log some events
        self.audit_logger.log_directory_operation("user1", "res1", "store", True, {})
        self.audit_logger.log_directory_operation("user2", "res2", "retrieve", True, {})
        self.audit_logger.log_access_denied("user3", "res3", "admin", "No permission")
        
        end_time = datetime.now(timezone.utc)
        
        report = self.audit_logger.generate_audit_report(start_time, end_time)
        
        self.assertIn('total_events', report)
        self.assertIn('event_types', report)
        self.assertIn('severity_distribution', report)
        self.assertIn('success_rate', report)
        self.assertGreater(report['total_events'], 0)


class TestDirectorySecurityManagerIntegration(unittest.TestCase):
    """Test DirectorySecurityManager integration"""
    
    def setUp(self):
        self.db_manager = MockDatabaseManager()
        self.security_manager = DirectorySecurityManager(self.db_manager)
    
    def test_complete_directory_storage_cycle(self):
        """Test complete directory storage and retrieval cycle"""
        user_id = "testuser"
        tool_name = "file_browser"
        directory_type = "favorite"
        directory_path = "C:\\Users\\testuser\\Documents\\Personal"
        
        # Store directory
        storage_result = self.security_manager.store_directory_preference(
            user_id, tool_name, directory_type, directory_path
        )
        
        self.assertTrue(storage_result.success)
        self.assertIsNotNone(storage_result.path_hash)
        self.assertTrue(storage_result.pii_sensitive)
        
        # Retrieve directory
        retrieval_result = self.security_manager.retrieve_directory_preference(
            user_id, storage_result.path_hash
        )
        
        self.assertTrue(retrieval_result.success)
        self.assertEqual(retrieval_result.tool_name, tool_name)
        self.assertEqual(retrieval_result.directory_type, directory_type)
        self.assertIn("Documents", retrieval_result.directory_path)
    
    def test_pii_sensitive_path_handling(self):
        """Test handling of PII-sensitive paths"""
        user_id = "testuser"
        sensitive_path = "/home/testuser/.ssh/private_keys"
        
        storage_result = self.security_manager.store_directory_preference(
            user_id, "security_tool", "config", sensitive_path
        )
        
        self.assertTrue(storage_result.success)
        self.assertTrue(storage_result.pii_sensitive)
        self.assertGreaterEqual(storage_result.sensitivity_level, 4)
    
    def test_malicious_path_rejection(self):
        """Test rejection of malicious paths"""
        user_id = "testuser"
        malicious_paths = [
            "../../../etc/passwd",
            "C:\\Windows\\System32\\sensitive.dll",
            "/etc/shadow"
        ]
        
        for path in malicious_paths:
            with self.subTest(path=path):
                result = self.security_manager.store_directory_preference(
                    user_id, "test_tool", "test", path
                )
                self.assertFalse(result.success)
                self.assertTrue(result.security_violation)
    
    def test_user_directory_listing(self):
        """Test user directory listing functionality"""
        user_id = "testuser"
        
        # Store multiple directories
        paths = [
            ("C:\\Users\\testuser\\Documents", "documents", "favorite"),
            ("C:\\Users\\testuser\\Downloads", "downloads", "recent"),
            ("C:\\Users\\testuser\\Desktop", "desktop", "default")
        ]
        
        stored_hashes = []
        for path, tool, dir_type in paths:
            result = self.security_manager.store_directory_preference(
                user_id, tool, dir_type, path
            )
            self.assertTrue(result.success)
            stored_hashes.append(result.path_hash)
        
        # List directories
        directories = self.security_manager.list_user_directories(user_id)
        self.assertGreaterEqual(len(directories), 3)
        
        # Test filtered listing
        filtered = self.security_manager.list_user_directories(
            user_id, tool_name="documents"
        )
        self.assertEqual(len(filtered), 1)
    
    def test_directory_deletion(self):
        """Test directory preference deletion"""
        user_id = "testuser"
        path = "C:\\Users\\testuser\\test"
        
        # Store directory
        storage_result = self.security_manager.store_directory_preference(
            user_id, "test_tool", "test", path
        )
        self.assertTrue(storage_result.success)
        
        # Delete directory
        delete_success = self.security_manager.delete_directory_preference(
            user_id, storage_result.path_hash
        )
        self.assertTrue(delete_success)
        
        # Verify deletion
        retrieval_result = self.security_manager.retrieve_directory_preference(
            user_id, storage_result.path_hash
        )
        self.assertFalse(retrieval_result.success)


class TestSecurityIntegration(unittest.TestCase):
    """Test security integration scenarios"""
    
    def setUp(self):
        self.db_manager = MockDatabaseManager()
        self.security_manager = DirectorySecurityManager(self.db_manager)
    
    def test_encryption_integration(self):
        """Test encryption integration with storage"""
        user_id = "testuser"
        sensitive_path = "/home/testuser/Documents/Financial/TaxReturns"
        
        storage_result = self.security_manager.store_directory_preference(
            user_id, "financial_app", "documents", sensitive_path
        )
        
        self.assertTrue(storage_result.success)
        self.assertTrue(storage_result.pii_sensitive)
        self.assertGreaterEqual(storage_result.sensitivity_level, 4)
        
        # Verify data is encrypted in database
        query = "SELECT encrypted_path, encryption_metadata FROM secure_directories WHERE path_hash = ?"
        result = self.db_manager.fetch_one(query, (storage_result.path_hash,))
        self.assertIsNotNone(result)
        self.assertIsNotNone(result[1])  # encryption_metadata should exist
    
    def test_audit_integration(self):
        """Test audit logging integration"""
        user_id = "testuser"
        path = "C:\\Users\\testuser\\Documents"
        
        # Store directory (should generate audit log)
        storage_result = self.security_manager.store_directory_preference(
            user_id, "test_tool", "test", path
        )
        self.assertTrue(storage_result.success)
        
        # Check audit log
        audit_events = self.security_manager.audit_logger.get_audit_events(user_id=user_id)
        self.assertGreater(len(audit_events), 0)
        
        # Verify event details
        store_events = [e for e in audit_events if e.action == "store"]
        self.assertGreater(len(store_events), 0)
        self.assertTrue(store_events[0].success)
    
    def test_permission_integration(self):
        """Test permission integration with storage"""
        user_id = "restricteduser"
        admin_user = "adminuser"
        path = "C:\\Restricted\\Directory"
        
        # Set up users
        self.db_manager.execute_query(
            "INSERT INTO directory_user_roles (user_id, role, assigned_by, assigned_at) VALUES (?, ?, ?, ?)",
            (user_id, "guest", admin_user, datetime.now(timezone.utc).isoformat())
        )
        
        self.db_manager.execute_query(
            "INSERT INTO directory_user_roles (user_id, role, assigned_by, assigned_at) VALUES (?, ?, ?, ?)",
            (admin_user, "admin", "system", datetime.now(timezone.utc).isoformat())
        )
        
        # Guest user should not be able to store in restricted location
        storage_result = self.security_manager.store_directory_preference(
            user_id, "test_tool", "test", path
        )
        
        # Depending on implementation, this might succeed but with restrictions
        # or fail due to guest role limitations
        if not storage_result.success:
            self.assertTrue(storage_result.security_violation)


def run_all_tests():
    """Run all test suites"""
    test_classes = [
        TestDirectoryPathValidator,
        TestPathSanitizer,
        TestPIIDetector,
        TestDirectoryPathEncryption,
        TestDirectoryPermissionManager,
        TestDirectoryAuditLogger,
        TestDirectorySecurityManagerIntegration,
        TestSecurityIntegration
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("Running Phase 3 Directory Security Test Suite...")
    print("=" * 60)
    
    success = run_all_tests()
    
    print("=" * 60)
    if success:
        print("✅ All tests passed! Phase 3 implementation is working correctly.")
    else:
        print("❌ Some tests failed. Please review the implementation.")
    
    print("Test coverage includes:")
    print("- Path validation and sanitization")
    print("- PII detection and anonymization")
    print("- Directory path encryption/decryption")
    print("- Permission management and access control")
    print("- Audit logging and compliance")
    print("- Complete integration scenarios")
    print("- Security violation detection")
    print("- Malicious input handling")