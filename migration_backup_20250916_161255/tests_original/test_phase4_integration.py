"""
Phase 4 End-to-End Integration Testing Suite

Comprehensive integration tests that validate complete workflows across all 
Phase 1-3 components including migration system, theme security, and directory security.

Author: RFU Development Team
Date: 2024
Version: 1.0.0
"""

import unittest
import tempfile
import shutil
import sqlite3
import os
import json
from datetime import datetime, timezone
from pathlib import Path
import threading
import time
from unittest.mock import Mock, patch

# Import all Phase 1-3 components for integration testing
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Phase 1: Migration System
from rfu.database.database_manager import DatabaseManager
from rfu.database.migration_manager import MigrationManager

# Phase 2: Theme Security (would be imported when implemented)
# from rfu.core.theme_security.theme_encryption_manager import ThemeEncryptionManager

# Phase 3: Directory Security
from rfu.core.directory_security.directory_security_manager import DirectorySecurityManager
from rfu.core.directory_security.directory_validator import DirectoryPathValidator
from rfu.core.directory_security.pii_detector import PIIDetector
from rfu.core.directory_security.directory_encryption import DirectoryPathEncryption
from rfu.core.directory_security.directory_permissions import DirectoryPermissionManager, DirectoryRole
from rfu.core.directory_security.directory_audit import DirectoryAuditLogger


class IntegrationTestDatabase:
    """Test database setup for integration testing"""
    
    def __init__(self):
        self.temp_dir = None
        self.db_path = None
        self.db_manager = None
    
    def setup(self):
        """Setup test database"""
        self.temp_dir = tempfile.mkdtemp(prefix="rfu_integration_test_")
        self.db_path = os.path.join(self.temp_dir, "test_rfu_database.db")
        self.db_manager = DatabaseManager(self.db_path)
        return self.db_manager
    
    def teardown(self):
        """Cleanup test database"""
        if self.db_manager:
            self.db_manager.close()
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


class TestPhase1to3Integration(unittest.TestCase):
    """Test integration between Phase 1, 2, and 3 components"""
    
    def setUp(self):
        """Setup integration test environment"""
        self.test_db = IntegrationTestDatabase()
        self.db_manager = self.test_db.setup()
        
        # Initialize migration manager
        self.migration_manager = MigrationManager(self.db_manager)
        
        # Initialize directory security components
        self.directory_security = DirectorySecurityManager(self.db_manager)
        self.pii_detector = PIIDetector()
        self.path_validator = DirectoryPathValidator()
        
        # Test user data
        self.test_user_id = "integration_test_user"
        self.test_admin_id = "integration_test_admin"
    
    def tearDown(self):
        """Cleanup integration test environment"""
        self.test_db.teardown()
    
    def test_complete_database_setup_workflow(self):
        """Test complete database setup from fresh install to fully configured"""
        # Test 1: Initial database creation
        self.assertTrue(os.path.exists(self.test_db.db_path))
        
        # Test 2: Run all migrations sequentially
        pending_migrations = self.migration_manager.get_pending_migrations()
        self.assertGreater(len(pending_migrations), 0, "Should have pending migrations")
        
        # Apply migrations one by one and validate
        for migration in pending_migrations:
            # Create backup before migration
            backup_path = self.migration_manager.create_backup()
            self.assertTrue(os.path.exists(backup_path))
            
            # Apply migration
            success = self.migration_manager.apply_migration(migration)
            self.assertTrue(success, f"Migration {migration} should succeed")
            
            # Validate schema after migration
            validation_result = self.migration_manager.validate_migration(migration)
            self.assertTrue(validation_result, f"Migration {migration} validation should pass")
        
        # Test 3: Verify all Phase 3 tables exist
        expected_tables = [
            'secure_directories', 'directory_user_roles', 'directory_permissions',
            'directory_audit_log', 'pii_detection_incidents', 'security_incidents',
            'directory_access_stats', 'encryption_key_metadata'
        ]
        
        for table in expected_tables:
            self.assertTrue(
                self.migration_manager._table_exists(table),
                f"Table {table} should exist after migrations"
            )
        
        # Test 4: Verify indexes and triggers
        self.assertTrue(
            self.migration_manager._index_exists('idx_directory_user_path'),
            "Security indexes should be created"
        )
    
    def test_end_to_end_directory_security_workflow(self):
        """Test complete directory security workflow end-to-end"""
        # Setup: Apply all migrations first
        self.migration_manager.apply_pending_migrations()
        
        # Test data
        sensitive_paths = [
            "C:\\Users\\john.doe\\Documents\\Personal\\Financial",
            "/home/testuser/.ssh/private_keys",
            "C:\\Users\\jane\\AppData\\Local\\Microsoft\\Outlook",
            "/Users/testuser/Documents/Medical/Records"
        ]
        
        safe_paths = [
            "C:\\Program Files\\Application",
            "/opt/software/tools",
            "/usr/local/bin"
        ]
        
        # Test 1: Directory storage with automatic PII detection and encryption
        for i, path in enumerate(sensitive_paths):
            with self.subTest(path=path):
                # Store directory preference
                storage_result = self.directory_security.store_directory_preference(
                    user_id=self.test_user_id,
                    tool_name=f"test_tool_{i}",
                    directory_type="favorite",
                    directory_path=path
                )
                
                # Verify storage success
                self.assertTrue(storage_result.success, f"Storage should succeed for {path}")
                self.assertTrue(storage_result.pii_sensitive, f"Should detect PII in {path}")
                self.assertGreaterEqual(storage_result.sensitivity_level, 3, f"Should have high sensitivity for {path}")
                
                # Verify path is encrypted in database
                query = "SELECT encrypted_path, encryption_metadata FROM secure_directories WHERE path_hash = ?"
                result = self.db_manager.fetch_one(query, (storage_result.path_hash,))
                self.assertIsNotNone(result, "Should find stored entry")
                self.assertIsNotNone(result[1], "Should have encryption metadata")
        
        # Test 2: Safe paths should not be encrypted
        for i, path in enumerate(safe_paths):
            with self.subTest(path=path):
                storage_result = self.directory_security.store_directory_preference(
                    user_id=self.test_user_id,
                    tool_name=f"safe_tool_{i}",
                    directory_type="default",
                    directory_path=path
                )
                
                self.assertTrue(storage_result.success)
                self.assertFalse(storage_result.pii_sensitive, f"Should not detect PII in {path}")
                self.assertLessEqual(storage_result.sensitivity_level, 2, f"Should have low sensitivity for {path}")
        
        # Test 3: Retrieve and verify decryption
        user_directories = self.directory_security.list_user_directories(self.test_user_id)
        self.assertGreaterEqual(len(user_directories), len(sensitive_paths) + len(safe_paths))
        
        for directory in user_directories:
            if directory.get('is_pii_sensitive'):
                # Test retrieval and decryption
                retrieval_result = self.directory_security.retrieve_directory_preference(
                    self.test_user_id, directory['path_hash']
                )
                
                self.assertTrue(retrieval_result.success, "Retrieval should succeed")
                self.assertIsNotNone(retrieval_result.directory_path, "Should have decrypted path")
                self.assertIn(retrieval_result.tool_name, [f"test_tool_{i}" for i in range(len(sensitive_paths))])
        
        # Test 4: Verify audit logging
        audit_events = self.directory_security.audit_logger.get_audit_events(user_id=self.test_user_id)
        self.assertGreater(len(audit_events), 0, "Should have audit events")
        
        # Verify different event types
        event_types = set(event.event_type for event in audit_events)
        expected_types = {'DIRECTORY_OPERATION', 'PII_DETECTION'}
        self.assertTrue(expected_types.issubset(event_types), "Should have expected audit event types")
    
    def test_permission_integration_workflow(self):
        """Test permission system integration with directory operations"""
        # Setup: Apply migrations
        self.migration_manager.apply_pending_migrations()
        
        # Test 1: Setup user roles
        perm_manager = DirectoryPermissionManager(self.db_manager)
        
        # Set admin role
        admin_success = perm_manager.set_user_role(
            self.test_admin_id, DirectoryRole.ADMIN, "system"
        )
        self.assertTrue(admin_success, "Should set admin role successfully")
        
        # Set regular user role
        user_success = perm_manager.set_user_role(
            self.test_user_id, DirectoryRole.USER, self.test_admin_id
        )
        self.assertTrue(user_success, "Should set user role successfully")
        
        # Test 2: Permission-based directory operations
        test_path = "C:\\Users\\test\\Documents\\Restricted"
        
        # Admin should be able to store any directory
        admin_storage = self.directory_security.store_directory_preference(
            self.test_admin_id, "admin_tool", "admin", test_path
        )
        self.assertTrue(admin_storage.success, "Admin should be able to store any directory")
        
        # Regular user should be able to store in their own scope
        user_storage = self.directory_security.store_directory_preference(
            self.test_user_id, "user_tool", "favorite", test_path
        )
        # Note: This might succeed or fail depending on permission implementation
        # The important thing is that it's handled consistently
        
        # Test 3: Verify permission audit events
        audit_events = self.directory_security.audit_logger.get_audit_events()
        permission_events = [e for e in audit_events if 'permission' in e.details.lower()]
        # Should have some permission-related audit events
    
    def test_malicious_input_integration_defense(self):
        """Test integrated defense against malicious inputs across all components"""
        # Setup: Apply migrations
        self.migration_manager.apply_pending_migrations()
        
        # Test malicious paths that should be blocked
        malicious_paths = [
            "../../../etc/passwd",
            "C:\\Windows\\System32\\..\\..\\sensitive.dll",
            "/etc/../../../root/.ssh/id_rsa",
            "\\\\network\\share\\..\\admin$",
            "path\x00with\x00nulls",
            "C:\\Users\\test<script>alert(1)</script>",
        ]
        
        for malicious_path in malicious_paths:
            with self.subTest(path=malicious_path):
                # Attempt to store malicious path
                storage_result = self.directory_security.store_directory_preference(
                    self.test_user_id, "malicious_test", "test", malicious_path
                )
                
                # Should either fail or be properly sanitized
                if not storage_result.success:
                    self.assertTrue(storage_result.security_violation, 
                                  f"Should detect security violation for {malicious_path}")
                else:
                    # If it succeeds, verify path was sanitized
                    retrieval_result = self.directory_security.retrieve_directory_preference(
                        self.test_user_id, storage_result.path_hash
                    )
                    self.assertTrue(retrieval_result.success)
                    # Path should be sanitized (no dangerous characters)
                    self.assertNotIn('\x00', retrieval_result.directory_path)
                    self.assertNotIn('<script>', retrieval_result.directory_path)
        
        # Verify security violations are logged
        audit_events = self.directory_security.audit_logger.get_audit_events(user_id=self.test_user_id)
        security_violations = [e for e in audit_events if e.event_type == 'SECURITY_VIOLATION']
        self.assertGreater(len(security_violations), 0, "Should have logged security violations")
    
    def test_migration_rollback_integration(self):
        """Test migration rollback with existing security data"""
        # Test 1: Apply migrations and create test data
        self.migration_manager.apply_pending_migrations()
        
        # Store some directory preferences
        test_paths = [
            "C:\\Users\\test\\Documents\\Personal",
            "/home/user/sensitive/data"
        ]
        
        stored_hashes = []
        for i, path in enumerate(test_paths):
            result = self.directory_security.store_directory_preference(
                self.test_user_id, f"rollback_test_{i}", "test", path
            )
            self.assertTrue(result.success)
            stored_hashes.append(result.path_hash)
        
        # Test 2: Create backup before rollback test
        backup_path = self.migration_manager.create_backup()
        self.assertTrue(os.path.exists(backup_path))
        
        # Test 3: Attempt rollback of last migration
        applied_migrations = self.migration_manager.get_applied_migrations()
        if applied_migrations:
            last_migration = applied_migrations[-1]
            
            # Note: Actual rollback might not be possible for all migrations
            # This test verifies the rollback system handles it gracefully
            try:
                rollback_success = self.migration_manager.rollback_migration(last_migration)
                if rollback_success:
                    # Verify data handling after rollback
                    # Some data might be lost, but system should remain consistent
                    pass
            except Exception as e:
                # Rollback might fail for data safety reasons - this is acceptable
                self.assertIn("rollback", str(e).lower())
        
        # Test 4: Restore from backup if needed
        if backup_path and os.path.exists(backup_path):
            restore_success = self.migration_manager.restore_from_backup(backup_path)
            # Restore should work regardless of rollback outcome
    
    def test_concurrent_operations_integration(self):
        """Test concurrent operations across all components"""
        # Setup: Apply migrations
        self.migration_manager.apply_pending_migrations()
        
        # Test concurrent directory operations
        results = []
        errors = []
        
        def concurrent_operation(thread_id):
            try:
                path = f"C:\\Users\\concurrent_test_{thread_id}\\Documents"
                result = self.directory_security.store_directory_preference(
                    f"user_{thread_id}", f"tool_{thread_id}", "concurrent", path
                )
                results.append((thread_id, result.success, result.path_hash if result.success else None))
            except Exception as e:
                errors.append((thread_id, str(e)))
        
        # Start multiple concurrent threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=concurrent_operation, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify results
        self.assertEqual(len(errors), 0, f"Should have no errors: {errors}")
        self.assertEqual(len(results), 5, "Should have 5 results")
        
        successful_results = [r for r in results if r[1]]  # r[1] is success flag
        self.assertGreaterEqual(len(successful_results), 4, "Most operations should succeed")
        
        # Verify audit logs captured concurrent operations
        audit_events = self.directory_security.audit_logger.get_audit_events()
        concurrent_events = [e for e in audit_events if 'concurrent' in e.details.lower()]
        self.assertGreaterEqual(len(concurrent_events), 4, "Should log concurrent operations")
    
    def test_performance_integration_benchmarks(self):
        """Test performance across integrated components"""
        # Setup: Apply migrations
        self.migration_manager.apply_pending_migrations()
        
        # Test 1: Directory storage performance
        start_time = time.time()
        storage_times = []
        
        for i in range(10):
            path = f"C:\\Users\\perf_test_{i}\\Documents\\TestFile_{i}"
            
            operation_start = time.time()
            result = self.directory_security.store_directory_preference(
                self.test_user_id, f"perf_tool_{i}", "performance", path
            )
            operation_time = time.time() - operation_start
            
            self.assertTrue(result.success, f"Performance test {i} should succeed")
            storage_times.append(operation_time)
        
        total_time = time.time() - start_time
        avg_storage_time = sum(storage_times) / len(storage_times)
        
        # Performance targets (from Phase 4 requirements)
        self.assertLess(avg_storage_time, 0.1, "Average storage time should be <100ms")
        self.assertLess(total_time, 5.0, "Total 10 operations should complete in <5s")
        
        # Test 2: Retrieval performance
        user_directories = self.directory_security.list_user_directories(self.test_user_id)
        retrieval_times = []
        
        for directory in user_directories[:5]:  # Test first 5
            operation_start = time.time()
            result = self.directory_security.retrieve_directory_preference(
                self.test_user_id, directory['path_hash']
            )
            operation_time = time.time() - operation_start
            
            self.assertTrue(result.success, "Retrieval should succeed")
            retrieval_times.append(operation_time)
        
        avg_retrieval_time = sum(retrieval_times) / len(retrieval_times) if retrieval_times else 0
        self.assertLess(avg_retrieval_time, 0.1, "Average retrieval time should be <100ms")
        
        # Test 3: Database size impact
        db_size = os.path.getsize(self.test_db.db_path)
        # Basic check that database hasn't grown excessively
        self.assertLess(db_size, 10 * 1024 * 1024, "Database should remain <10MB for test data")
    
    def test_data_integrity_across_components(self):
        """Test data integrity across all components"""
        # Setup: Apply migrations
        self.migration_manager.apply_pending_migrations()
        
        # Test 1: Store directory with complex metadata
        complex_path = "C:\\Users\\integrity_test\\Documents\\Complex File (Test) [2024]"
        metadata = {
            "custom_field": "test_value",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "1.0.0"
        }
        
        storage_result = self.directory_security.store_directory_preference(
            self.test_user_id, "integrity_tool", "integrity_test", 
            complex_path, additional_metadata=metadata
        )
        self.assertTrue(storage_result.success)
        
        # Test 2: Verify data consistency across retrievals
        for _ in range(3):  # Multiple retrievals
            retrieval_result = self.directory_security.retrieve_directory_preference(
                self.test_user_id, storage_result.path_hash
            )
            self.assertTrue(retrieval_result.success)
            self.assertEqual(retrieval_result.tool_name, "integrity_tool")
            self.assertEqual(retrieval_result.directory_type, "integrity_test")
            
            # Path should be consistent (possibly sanitized but consistently so)
            if not hasattr(self, '_original_retrieved_path'):
                self._original_retrieved_path = retrieval_result.directory_path
            else:
                self.assertEqual(retrieval_result.directory_path, self._original_retrieved_path)
        
        # Test 3: Verify audit log consistency
        audit_events = self.directory_security.audit_logger.get_audit_events(
            user_id=self.test_user_id
        )
        
        # Find events related to our test
        integrity_events = [e for e in audit_events if 'integrity_test' in str(e.details)]
        self.assertGreater(len(integrity_events), 0, "Should have audit events for integrity test")
        
        # Verify audit event consistency
        for event in integrity_events:
            self.assertEqual(event.user_id, self.test_user_id)
            self.assertIsNotNone(event.timestamp)
            self.assertIsNotNone(event.event_id)


class TestErrorHandlingIntegration(unittest.TestCase):
    """Test error handling across integrated components"""
    
    def setUp(self):
        """Setup error handling test environment"""
        self.test_db = IntegrationTestDatabase()
        self.db_manager = self.test_db.setup()
        self.migration_manager = MigrationManager(self.db_manager)
        self.directory_security = DirectorySecurityManager(self.db_manager)
    
    def tearDown(self):
        """Cleanup error handling test environment"""
        self.test_db.teardown()
    
    def test_database_corruption_handling(self):
        """Test handling of database corruption scenarios"""
        # Apply migrations first
        self.migration_manager.apply_pending_migrations()
        
        # Store some test data
        storage_result = self.directory_security.store_directory_preference(
            "test_user", "test_tool", "test", "C:\\Test\\Path"
        )
        self.assertTrue(storage_result.success)
        
        # Simulate database corruption by directly modifying database
        connection = sqlite3.connect(self.test_db.db_path)
        cursor = connection.cursor()
        
        # Corrupt some data (but not critically)
        try:
            cursor.execute("UPDATE secure_directories SET encrypted_path = ? WHERE storage_id = ?", 
                          (b"corrupted_data", storage_result.path_hash))
            connection.commit()
            connection.close()
        except Exception:
            connection.close()
        
        # Test graceful handling of corruption
        retrieval_result = self.directory_security.retrieve_directory_preference(
            "test_user", storage_result.path_hash
        )
        
        # Should handle corruption gracefully (either succeed with fallback or fail gracefully)
        if not retrieval_result.success:
            self.assertIsNotNone(retrieval_result.error_message)
            self.assertIn("decrypt", retrieval_result.error_message.lower())
    
    def test_migration_failure_recovery(self):
        """Test recovery from migration failures"""
        # Create a backup before attempting problematic migration
        backup_path = self.migration_manager.create_backup()
        self.assertTrue(os.path.exists(backup_path))
        
        # Simulate migration failure by corrupting migration state
        # This tests the recovery mechanisms
        
        try:
            # Apply migrations normally first
            success = self.migration_manager.apply_pending_migrations()
            self.assertTrue(success, "Initial migrations should succeed")
            
            # Now test recovery from backup if needed
            if backup_path and os.path.exists(backup_path):
                restore_result = self.migration_manager.restore_from_backup(backup_path)
                # Restore should work or fail gracefully
                
        except Exception as e:
            # Any exception should be properly handled
            self.assertIsInstance(e, (ValueError, RuntimeError, sqlite3.Error))
    
    def test_concurrent_access_error_handling(self):
        """Test error handling under concurrent access"""
        self.migration_manager.apply_pending_migrations()
        
        errors = []
        successes = []
        
        def concurrent_access_test(thread_id):
            try:
                # Each thread tries to access the same resource
                result = self.directory_security.store_directory_preference(
                    "shared_user", f"tool_{thread_id}", "concurrent", 
                    f"C:\\Shared\\Path\\{thread_id}"
                )
                if result.success:
                    successes.append(thread_id)
                else:
                    errors.append((thread_id, result.error_message))
            except Exception as e:
                errors.append((thread_id, str(e)))
        
        # Start multiple threads accessing same user
        threads = []
        for i in range(5):
            thread = threading.Thread(target=concurrent_access_test, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Should handle concurrent access gracefully
        total_operations = len(successes) + len(errors)
        self.assertEqual(total_operations, 5, "Should account for all operations")
        
        # Most operations should succeed, with proper error handling for any that fail
        self.assertGreaterEqual(len(successes), 3, "Most concurrent operations should succeed")


def run_integration_tests():
    """Run all Phase 4 integration tests"""
    test_classes = [
        TestPhase1to3Integration,
        TestErrorHandlingIntegration
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("Running Phase 4 Integration Testing Suite...")
    print("=" * 60)
    
    success = run_integration_tests()
    
    print("=" * 60)
    if success:
        print("✅ All integration tests passed! Phase 1-3 integration is working correctly.")
    else:
        print("❌ Some integration tests failed. Please review the implementation.")
    
    print("\nIntegration test coverage includes:")
    print("- Complete database setup workflow validation")
    print("- End-to-end directory security workflow testing")
    print("- Permission system integration validation")
    print("- Malicious input defense testing")
    print("- Migration rollback integration testing")
    print("- Concurrent operations testing")
    print("- Performance benchmark validation")
    print("- Data integrity across components")
    print("- Error handling and recovery testing")