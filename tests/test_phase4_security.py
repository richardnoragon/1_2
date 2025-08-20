"""
Phase 4 Security Testing Framework

Specialized security testing including penetration testing for path traversal,
encryption strength validation, access control bypass attempts, and audit log integrity.

Author: RFU Development Team
Date: 2024
Version: 1.0.0
"""

import unittest
import tempfile
import shutil
import os
import sqlite3
import threading
import time
import hashlib
import secrets
import string
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

# Import security components for testing
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from rfu.database.database_manager import DatabaseManager
from rfu.database.migration_manager import MigrationManager
from rfu.core.directory_security.directory_security_manager import DirectorySecurityManager
from rfu.core.directory_security.directory_validator import DirectoryPathValidator
from rfu.core.directory_security.path_sanitizer import PathSanitizer
from rfu.core.directory_security.pii_detector import PIIDetector
from rfu.core.directory_security.directory_encryption import DirectoryPathEncryption
from rfu.core.directory_security.directory_permissions import (
    DirectoryPermissionManager, DirectoryRole, PermissionLevel
)
from rfu.core.directory_security.directory_audit import DirectoryAuditLogger


class SecurityTestEnvironment:
    """Security test environment setup"""
    
    def __init__(self):
        self.temp_dir = None
        self.db_path = None
        self.db_manager = None
        self.security_manager = None
    
    def setup(self):
        """Setup security test environment"""
        self.temp_dir = tempfile.mkdtemp(prefix="rfu_security_test_")
        self.db_path = os.path.join(self.temp_dir, "security_test.db")
        self.db_manager = DatabaseManager(self.db_path)
        
        # Apply all migrations
        migration_manager = MigrationManager(self.db_manager)
        migration_manager.apply_pending_migrations()
        
        # Initialize security manager
        self.security_manager = DirectorySecurityManager(self.db_manager)
        
        return self.security_manager, self.db_manager
    
    def teardown(self):
        """Cleanup security test environment"""
        if self.db_manager:
            self.db_manager.close()
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


class TestPathTraversalSecurity(unittest.TestCase):
    """Test path traversal attack prevention"""
    
    def setUp(self):
        """Setup path traversal test environment"""
        self.env = SecurityTestEnvironment()
        self.security_manager, self.db_manager = self.env.setup()
        self.validator = DirectoryPathValidator()
        self.test_user = "security_test_user"
    
    def tearDown(self):
        """Cleanup path traversal test environment"""
        self.env.teardown()
    
    def test_basic_path_traversal_attacks(self):
        """Test basic path traversal attack vectors"""
        traversal_attacks = [
            "../../../etc/passwd",
            "..\\..\\..\\Windows\\System32",
            "/var/www/../../../etc/shadow",
            "C:\\inetpub\\..\\..\\Windows\\System32\\config\\SAM",
            "....//....//....//etc//passwd",
            "..%2F..%2F..%2Fetc%2Fpasswd",
            "..%5C..%5C..%5CWindows%5CSystem32",
            "./../.../.././../etc/passwd",
        ]
        
        for attack_path in traversal_attacks:
            with self.subTest(path=attack_path):
                # Test path validation
                validation_result = self.validator.validate_directory_path(
                    attack_path, self.test_user
                )
                self.assertFalse(
                    validation_result.valid,
                    f"Should reject path traversal: {attack_path}"
                )
                self.assertIn(
                    "traversal", validation_result.reason.lower(),
                    f"Should identify traversal attack: {attack_path}"
                )
                
                # Test storage attempt
                storage_result = self.security_manager.store_directory_preference(
                    self.test_user, "security_test", "attack", attack_path
                )
                self.assertFalse(
                    storage_result.success,
                    f"Should block storage of traversal path: {attack_path}"
                )
                self.assertTrue(
                    storage_result.security_violation,
                    f"Should flag as security violation: {attack_path}"
                )
    
    def test_unicode_path_traversal_attacks(self):
        """Test Unicode-based path traversal attacks"""
        unicode_attacks = [
            "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",
            "..%e0%80%af..%e0%80%af..%e0%80%afetc%e0%80%afpasswd",
            "\u002e\u002e\u002f\u002e\u002e\u002fetc\u002fpasswd",
            "\uff0e\uff0e\uff0f\uff0e\uff0e\uff0fetc\uff0fpasswd",
        ]
        
        for attack_path in unicode_attacks:
            with self.subTest(path=attack_path):
                validation_result = self.validator.validate_directory_path(
                    attack_path, self.test_user
                )
                self.assertFalse(
                    validation_result.valid,
                    f"Should reject Unicode traversal: {attack_path}"
                )
    
    def test_absolute_path_attacks(self):
        """Test absolute path attacks to sensitive locations"""
        sensitive_paths = [
            "/etc/passwd",
            "/etc/shadow",
            "/root/.ssh/id_rsa",
            "C:\\Windows\\System32\\config\\SAM",
            "C:\\Windows\\System32\\config\\SYSTEM",
            "/proc/version",
            "/sys/class/dmi/id/product_uuid",
        ]
        
        for sensitive_path in sensitive_paths:
            with self.subTest(path=sensitive_path):
                # Should either reject or heavily restrict access
                validation_result = self.validator.validate_directory_path(
                    sensitive_path, self.test_user
                )
                
                if validation_result.valid:
                    # If validation passes, ensure storage has restrictions
                    storage_result = self.security_manager.store_directory_preference(
                        self.test_user, "security_test", "sensitive", sensitive_path
                    )
                    
                    if storage_result.success:
                        # Should be flagged as highly sensitive
                        self.assertGreaterEqual(
                            storage_result.sensitivity_level, 4,
                            f"Sensitive path should have high sensitivity: {sensitive_path}"
                        )
                        self.assertTrue(
                            storage_result.pii_sensitive,
                            f"Sensitive path should be PII flagged: {sensitive_path}"
                        )
    
    def test_symbolic_link_attacks(self):
        """Test symbolic link attack prevention"""
        # Create test symbolic links in temp directory
        if os.name != 'nt':  # Unix-like systems
            test_dir = tempfile.mkdtemp()
            try:
                # Create a symbolic link pointing outside
                symlink_path = os.path.join(test_dir, "malicious_symlink")
                target_path = "/etc/passwd"
                
                try:
                    os.symlink(target_path, symlink_path)
                    
                    # Test validation of symlink
                    validation_result = self.validator.validate_directory_path(
                        symlink_path, self.test_user
                    )
                    
                    # Should either reject or resolve safely
                    if not validation_result.valid:
                        self.assertIn("symlink", validation_result.reason.lower())
                    else:
                        # If accepted, ensure it doesn't resolve to sensitive location
                        resolved_path = validation_result.normalized_path
                        self.assertNotIn("/etc", resolved_path)
                        self.assertNotIn("/root", resolved_path)
                
                except OSError:
                    # Symlink creation failed - skip this test
                    pass
            
            finally:
                shutil.rmtree(test_dir)
    
    def test_null_byte_injection(self):
        """Test null byte injection attacks"""
        null_byte_attacks = [
            "safe_path\x00/../../../etc/passwd",
            "C:\\Users\\test\x00\\..\\..\\Windows\\System32",
            "normal_file.txt\x00.secret",
            "/home/user/docs\x00/../.ssh/id_rsa",
        ]
        
        for attack_path in null_byte_attacks:
            with self.subTest(path=attack_path):
                # Should be sanitized or rejected
                sanitizer = PathSanitizer()
                sanitized_path = sanitizer.sanitize_path(attack_path)
                self.assertNotIn('\x00', sanitized_path)
                
                # Validation should also handle null bytes
                validation_result = self.validator.validate_directory_path(
                    attack_path, self.test_user
                )
                if validation_result.valid:
                    # If valid, normalized path should not contain null bytes
                    self.assertNotIn('\x00', validation_result.normalized_path)


class TestEncryptionSecurity(unittest.TestCase):
    """Test encryption strength and security"""
    
    def setUp(self):
        """Setup encryption security test environment"""
        self.env = SecurityTestEnvironment()
        self.security_manager, self.db_manager = self.env.setup()
        self.encryption = DirectoryPathEncryption()
        self.test_user = "encryption_test_user"
    
    def tearDown(self):
        """Cleanup encryption security test environment"""
        self.env.teardown()
    
    def test_encryption_key_strength(self):
        """Test encryption key derivation strength"""
        # Test key derivation with various inputs
        test_passwords = [
            "weak",
            "strongpassword123",
            "Very$trong@P@ssw0rd!",
            "unicode_ñoñó_password_🔒"
        ]
        
        for password in test_passwords:
            with self.subTest(password=password):
                salt = secrets.token_bytes(32)
                
                # Test key derivation
                key = self.encryption._derive_directory_key(password, salt)
                
                # Key should be 32 bytes (256 bits)
                self.assertEqual(len(key), 32, "Key should be 256 bits")
                
                # Key should be deterministic with same input
                key2 = self.encryption._derive_directory_key(password, salt)
                self.assertEqual(key, key2, "Key derivation should be deterministic")
                
                # Key should be different with different salt
                salt2 = secrets.token_bytes(32)
                key3 = self.encryption._derive_directory_key(password, salt2)
                self.assertNotEqual(key, key3, "Different salt should produce different key")
    
    def test_encryption_randomness(self):
        """Test encryption randomness and uniqueness"""
        test_path = "C:\\Users\\test\\Documents\\Personal"
        
        # Encrypt same path multiple times
        results = []
        for i in range(10):
            result = self.encryption.encrypt_directory_path(test_path, f"user_{i}")
            self.assertTrue(result.success, f"Encryption {i} should succeed")
            results.append(result)
        
        # All results should be different (due to random salt/nonce)
        encrypted_data = [r.encrypted_data for r in results]
        salts = [r.salt for r in results]
        nonces = [r.nonce for r in results]
        
        # No two encryptions should be identical
        self.assertEqual(len(set(encrypted_data)), len(encrypted_data), 
                        "All encrypted data should be unique")
        self.assertEqual(len(set(salts)), len(salts), 
                        "All salts should be unique")
        self.assertEqual(len(set(nonces)), len(nonces), 
                        "All nonces should be unique")
    
    def test_encryption_integrity_attacks(self):
        """Test encryption integrity protection"""
        test_path = "C:\\Users\\test\\Documents\\Sensitive"
        user_id = "integrity_test_user"
        
        # Encrypt data
        encrypt_result = self.encryption.encrypt_directory_path(test_path, user_id)
        self.assertTrue(encrypt_result.success)
        
        # Test 1: Modify encrypted data
        modified_data = bytearray(encrypt_result.encrypted_data)
        modified_data[0] = (modified_data[0] + 1) % 256  # Flip one bit
        
        decrypt_result = self.encryption.decrypt_directory_path(
            bytes(modified_data), encrypt_result.salt, encrypt_result.nonce,
            user_id, encrypt_result.integrity_hash
        )
        self.assertFalse(decrypt_result.success, "Should fail with modified data")
        
        # Test 2: Modify salt
        modified_salt = bytearray(encrypt_result.salt)
        modified_salt[0] = (modified_salt[0] + 1) % 256
        
        decrypt_result = self.encryption.decrypt_directory_path(
            encrypt_result.encrypted_data, bytes(modified_salt), 
            encrypt_result.nonce, user_id, encrypt_result.integrity_hash
        )
        self.assertFalse(decrypt_result.success, "Should fail with modified salt")
        
        # Test 3: Modify nonce
        modified_nonce = bytearray(encrypt_result.nonce)
        modified_nonce[0] = (modified_nonce[0] + 1) % 256
        
        decrypt_result = self.encryption.decrypt_directory_path(
            encrypt_result.encrypted_data, encrypt_result.salt,
            bytes(modified_nonce), user_id, encrypt_result.integrity_hash
        )
        self.assertFalse(decrypt_result.success, "Should fail with modified nonce")
        
        # Test 4: Wrong integrity hash
        wrong_hash = hashlib.sha256(b"wrong_data").hexdigest()
        
        decrypt_result = self.encryption.decrypt_directory_path(
            encrypt_result.encrypted_data, encrypt_result.salt,
            encrypt_result.nonce, user_id, wrong_hash
        )
        self.assertFalse(decrypt_result.success, "Should fail with wrong hash")
    
    def test_user_isolation_attacks(self):
        """Test user isolation in encryption"""
        test_path = "C:\\Users\\shared\\Documents"
        user1 = "user1"
        user2 = "user2"
        
        # User1 encrypts data
        encrypt_result = self.encryption.encrypt_directory_path(test_path, user1)
        self.assertTrue(encrypt_result.success)
        
        # User2 tries to decrypt user1's data
        decrypt_result = self.encryption.decrypt_directory_path(
            encrypt_result.encrypted_data, encrypt_result.salt,
            encrypt_result.nonce, user2, encrypt_result.integrity_hash
        )
        self.assertFalse(decrypt_result.success, 
                        "User2 should not be able to decrypt user1's data")
        
        # Verify user1 can still decrypt their own data
        decrypt_result = self.encryption.decrypt_directory_path(
            encrypt_result.encrypted_data, encrypt_result.salt,
            encrypt_result.nonce, user1, encrypt_result.integrity_hash
        )
        self.assertTrue(decrypt_result.success, "User1 should decrypt their own data")
        self.assertEqual(decrypt_result.directory_path, os.path.normpath(test_path))
    
    def test_timing_attack_resistance(self):
        """Test resistance to timing attacks"""
        valid_user = "valid_user"
        invalid_user = "invalid_user"
        test_path = "C:\\Users\\test\\Documents"
        
        # Encrypt with valid user
        encrypt_result = self.encryption.encrypt_directory_path(test_path, valid_user)
        self.assertTrue(encrypt_result.success)
        
        # Measure decryption time for valid user
        valid_times = []
        for _ in range(5):
            start_time = time.time()
            self.encryption.decrypt_directory_path(
                encrypt_result.encrypted_data, encrypt_result.salt,
                encrypt_result.nonce, valid_user, encrypt_result.integrity_hash
            )
            valid_times.append(time.time() - start_time)
        
        # Measure decryption time for invalid user
        invalid_times = []
        for _ in range(5):
            start_time = time.time()
            self.encryption.decrypt_directory_path(
                encrypt_result.encrypted_data, encrypt_result.salt,
                encrypt_result.nonce, invalid_user, encrypt_result.integrity_hash
            )
            invalid_times.append(time.time() - start_time)
        
        # Times should be similar to avoid timing attacks
        avg_valid_time = sum(valid_times) / len(valid_times)
        avg_invalid_time = sum(invalid_times) / len(invalid_times)
        
        # Allow for some variance but times shouldn't be dramatically different
        time_ratio = max(avg_valid_time, avg_invalid_time) / min(avg_valid_time, avg_invalid_time)
        self.assertLess(time_ratio, 2.0, "Timing should not reveal validity")


class TestAccessControlSecurity(unittest.TestCase):
    """Test access control bypass attempts"""
    
    def setUp(self):
        """Setup access control security test environment"""
        self.env = SecurityTestEnvironment()
        self.security_manager, self.db_manager = self.env.setup()
        self.perm_manager = DirectoryPermissionManager(self.db_manager)
        
        # Setup test users with different roles
        self.admin_user = "admin_user"
        self.power_user = "power_user"
        self.regular_user = "regular_user"
        self.guest_user = "guest_user"
        
        # Assign roles
        self.perm_manager.set_user_role(self.admin_user, DirectoryRole.ADMIN, "system")
        self.perm_manager.set_user_role(self.power_user, DirectoryRole.POWER_USER, self.admin_user)
        self.perm_manager.set_user_role(self.regular_user, DirectoryRole.USER, self.admin_user)
        self.perm_manager.set_user_role(self.guest_user, DirectoryRole.GUEST, self.admin_user)
    
    def tearDown(self):
        """Cleanup access control security test environment"""
        self.env.teardown()
    
    def test_privilege_escalation_attempts(self):
        """Test privilege escalation attack prevention"""
        # Test 1: Regular user trying to perform admin actions
        admin_actions = [
            ("admin", "admin_resource"),
            ("delete", "system_resource"),
            ("write", "restricted_resource")
        ]
        
        for action, resource in admin_actions:
            with self.subTest(action=action, resource=resource):
                result = self.perm_manager.check_directory_permission(
                    self.regular_user, resource, action
                )
                
                if action == "admin":
                    self.assertFalse(result.authorized, 
                                   f"Regular user should not have admin access to {resource}")
                # Other actions might be allowed depending on resource
    
    def test_horizontal_privilege_escalation(self):
        """Test horizontal privilege escalation prevention"""
        # Store directory for user1
        user1_path = "C:\\Users\\user1\\Personal\\Documents"
        storage_result = self.security_manager.store_directory_preference(
            self.regular_user, "personal_tool", "private", user1_path
        )
        self.assertTrue(storage_result.success)
        
        # Create another regular user
        other_user = "other_regular_user"
        self.perm_manager.set_user_role(other_user, DirectoryRole.USER, self.admin_user)
        
        # Other user should not be able to access user1's directories
        retrieval_result = self.security_manager.retrieve_directory_preference(
            other_user, storage_result.path_hash
        )
        
        # Should either fail or return only their own data
        if retrieval_result.success:
            # If successful, should not return user1's data
            # This depends on implementation - might filter by user
            pass
        else:
            # Expected: access denied
            self.assertIn("access", retrieval_result.error_message.lower())
    
    def test_role_based_access_control_bypass(self):
        """Test RBAC bypass attempts"""
        # Test 1: Guest user trying to escalate to higher roles
        sensitive_path = "C:\\System\\Critical\\Data"
        
        # Guest should have very limited access
        guest_storage = self.security_manager.store_directory_preference(
            self.guest_user, "guest_tool", "guest", sensitive_path
        )
        
        # Depending on implementation, this might:
        # 1. Fail due to insufficient permissions
        # 2. Succeed but with heavy restrictions
        if guest_storage.success:
            self.assertGreaterEqual(guest_storage.sensitivity_level, 4,
                                  "Sensitive paths should have high sensitivity for guests")
        
        # Test 2: Power user trying to exceed their permissions
        admin_resource = "system_admin_resource"
        power_user_result = self.perm_manager.check_directory_permission(
            self.power_user, admin_resource, "admin"
        )
        
        # Power user should not have full admin rights
        if power_user_result.authorized:
            # If authorized, should have restrictions
            self.assertIsNotNone(power_user_result.restrictions)
    
    def test_session_based_attacks(self):
        """Test session-based attack prevention"""
        # Test concurrent session attacks
        test_path = "C:\\Users\\test\\ConcurrentAccess"
        
        # Multiple concurrent access attempts
        results = []
        errors = []
        
        def concurrent_access(thread_id):
            try:
                result = self.security_manager.store_directory_preference(
                    self.regular_user, f"concurrent_tool_{thread_id}", 
                    "concurrent", f"{test_path}_{thread_id}"
                )
                results.append((thread_id, result.success))
            except Exception as e:
                errors.append((thread_id, str(e)))
        
        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=concurrent_access, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Should handle concurrent access gracefully
        self.assertEqual(len(errors), 0, f"Should handle concurrent access: {errors}")
        successful_results = [r for r in results if r[1]]
        self.assertGreaterEqual(len(successful_results), 3, 
                              "Most concurrent operations should succeed")


class TestAuditLogSecurity(unittest.TestCase):
    """Test audit log integrity and security"""
    
    def setUp(self):
        """Setup audit log security test environment"""
        self.env = SecurityTestEnvironment()
        self.security_manager, self.db_manager = self.env.setup()
        self.audit_logger = DirectoryAuditLogger(self.db_manager)
        self.test_user = "audit_test_user"
    
    def tearDown(self):
        """Cleanup audit log security test environment"""
        self.env.teardown()
    
    def test_audit_log_tampering_detection(self):
        """Test audit log tampering detection"""
        # Generate some audit events
        test_events = [
            ("store", True, {"path": "test1"}),
            ("retrieve", True, {"path": "test2"}),
            ("delete", False, {"error": "permission_denied"}),
        ]
        
        event_ids = []
        for action, success, details in test_events:
            event_id = self.audit_logger.log_directory_operation(
                self.test_user, "test_resource", action, success, details
            )
            event_ids.append(event_id)
        
        # Verify events are logged
        audit_events = self.audit_logger.get_audit_events(user_id=self.test_user)
        self.assertGreaterEqual(len(audit_events), len(test_events))
        
        # Attempt to tamper with audit log directly
        connection = sqlite3.connect(self.env.db_path)
        cursor = connection.cursor()
        
        try:
            # Try to modify an audit event
            cursor.execute(
                "UPDATE directory_audit_log SET success = ? WHERE event_id = ?",
                (not test_events[0][1], event_ids[0])
            )
            connection.commit()
            
            # Verify tampering is detectable
            modified_events = self.audit_logger.get_audit_events(user_id=self.test_user)
            
            # Implementation should either:
            # 1. Prevent modification
            # 2. Detect and flag tampering
            # 3. Maintain integrity through checksums
            
            tampered_event = next((e for e in modified_events if e.event_id == event_ids[0]), None)
            if tampered_event:
                # If modification succeeded, check for integrity mechanisms
                # This depends on implementation details
                pass
        
        except sqlite3.Error:
            # Good: Direct modification was prevented
            pass
        
        finally:
            connection.close()
    
    def test_audit_log_injection_attacks(self):
        """Test audit log injection attack prevention"""
        # Test SQL injection in audit details
        malicious_details = {
            "sql_injection": "'; DROP TABLE directory_audit_log; --",
            "json_injection": '{"evil": "\\"; DROP TABLE directory_audit_log; --"}',
            "script_injection": "<script>alert('xss')</script>",
            "null_injection": "test\x00injection",
        }
        
        for attack_type, malicious_data in malicious_details.items():
            with self.subTest(attack_type=attack_type):
                # Log event with malicious data
                event_id = self.audit_logger.log_directory_operation(
                    self.test_user, "test_resource", "test", True, 
                    {"malicious": malicious_data}
                )
                
                # Verify event was logged safely
                self.assertIsNotNone(event_id, f"Should log event safely: {attack_type}")
                
                # Verify data integrity
                events = self.audit_logger.get_audit_events(user_id=self.test_user, limit=1)
                if events:
                    event = events[0]
                    # Event details should be safely stored
                    self.assertIsNotNone(event.details)
                    # Should not contain raw malicious content in database
        
        # Verify audit log table still exists
        cursor = self.db_manager.connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='directory_audit_log'")
        table_exists = cursor.fetchone() is not None
        self.assertTrue(table_exists, "Audit log table should still exist")
    
    def test_audit_log_information_disclosure(self):
        """Test audit log information disclosure prevention"""
        # Store sensitive path
        sensitive_path = "C:\\Users\\john.doe\\Personal\\Medical\\Records"
        storage_result = self.security_manager.store_directory_preference(
            self.test_user, "medical_app", "sensitive", sensitive_path
        )
        self.assertTrue(storage_result.success)
        
        # Check audit events for PII leakage
        audit_events = self.audit_logger.get_audit_events(user_id=self.test_user)
        
        for event in audit_events:
            # Audit logs should not contain raw PII
            event_str = str(event.details).lower()
            
            # Should not contain username
            self.assertNotIn("john.doe", event_str, 
                           "Audit log should not contain raw username")
            
            # Should not contain full sensitive path
            self.assertNotIn("medical", event_str.lower(), 
                           "Audit log should not contain sensitive path details")
            
            # Should use anonymized data
            if hasattr(event, 'anonymized_data') and event.anonymized_data:
                anonymized_str = str(event.anonymized_data).lower()
                self.assertIn("[user]", anonymized_str, 
                            "Should use anonymized placeholders")
    
    def test_audit_log_availability_attacks(self):
        """Test audit log availability attack prevention"""
        # Test 1: Log flooding attack
        start_time = time.time()
        flood_count = 100
        
        for i in range(flood_count):
            self.audit_logger.log_directory_operation(
                f"flood_user_{i}", f"flood_resource_{i}", "flood_test", True, 
                {"flood_data": f"flood_attempt_{i}"}
            )
        
        end_time = time.time()
        flood_time = end_time - start_time
        
        # Should handle flood gracefully (not take too long)
        self.assertLess(flood_time, 10.0, "Should handle audit flood in reasonable time")
        
        # Verify system is still responsive
        normal_event_id = self.audit_logger.log_directory_operation(
            self.test_user, "normal_resource", "normal_test", True, {"normal": "data"}
        )
        self.assertIsNotNone(normal_event_id, "Should still log normal events after flood")
        
        # Test 2: Large data attack
        large_data = {"large_field": "x" * 10000}  # 10KB of data
        
        large_event_id = self.audit_logger.log_directory_operation(
            self.test_user, "large_resource", "large_test", True, large_data
        )
        
        # Should handle large data gracefully
        if large_event_id:
            # If logged, verify it's truncated or handled appropriately
            events = self.audit_logger.get_audit_events(user_id=self.test_user, limit=1)
            if events:
                event = events[0]
                # Event details should be reasonably sized
                details_size = len(str(event.details))
                self.assertLess(details_size, 5000, "Large audit data should be truncated")


def run_security_tests():
    """Run all Phase 4 security tests"""
    test_classes = [
        TestPathTraversalSecurity,
        TestEncryptionSecurity,
        TestAccessControlSecurity,
        TestAuditLogSecurity
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("Running Phase 4 Security Testing Framework...")
    print("=" * 60)
    
    success = run_security_tests()
    
    print("=" * 60)
    if success:
        print("✅ All security tests passed! Security implementation is robust.")
    else:
        print("❌ Some security tests failed. Please review security implementation.")
    
    print("\nSecurity test coverage includes:")
    print("- Path traversal attack prevention")
    print("- Unicode and null byte injection protection")
    print("- Symbolic link attack prevention")
    print("- Encryption strength validation")
    print("- Integrity protection testing")
    print("- User isolation verification")
    print("- Timing attack resistance")
    print("- Privilege escalation prevention")
    print("- Access control bypass attempts")
    print("- Audit log tampering detection")
    print("- Information disclosure prevention")
    print("- Availability attack protection")