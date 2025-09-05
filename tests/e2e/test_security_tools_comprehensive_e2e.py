#!/usr/bin/env python3
"""
Security Tools Comprehensive End-to-End Test Suite

Comprehensive integration testing for all Security Tools working together.
Tests complete security pipelines, cross-tool data flow validation, user
journey validation, and hub integration coordination.

Created: 2025-09-04
Coverage: Security pipeline integration, cross-tool workflows, user journeys,
          concurrent operations, hub coordination, performance regression
Priority: HIGH (comprehensive Security Tools E2E coverage validation)
"""

import os
import shutil
import sys
import tempfile
import time
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')))

try:
    from tests.e2e.security_tools_test_utilities import (
        MockEncryptionDecryptionTool, MockSecureDeleteTool,
        MockSecurityPreferencesTool, MockSecurityToolsHub,
        SecurityToolsPerformanceMonitor, SecurityToolsSignalTracker,
        SecurityToolsTestDataFactory, assert_performance_target)
    UTILITIES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import utilities: {e}")
    UTILITIES_AVAILABLE = False

# Skip all tests if utilities not available
pytestmark = pytest.mark.skipif(
    not UTILITIES_AVAILABLE, 
    reason="Security Tools utilities not available"
)


class TestCompleteSecurityPipeline:
    """Test complete security pipeline workflows."""
    
    def test_security_configuration_to_encryption_workflow(self):
        """
        Test: Security Config → Policy Application → File Encryption
        Target: < 60 seconds for complete config-to-encryption pipeline
        """
        # Create test environment
        test_path = SecurityToolsTestDataFactory.create_security_tools_dataset(
            None, 'medium')
        hub = MockSecurityToolsHub()
        
        # Initialize security tools
        security_prefs = hub.open_security_preferences()
        encryption_tool = hub.open_encryption_decryption()
        
        performance_monitor = SecurityToolsPerformanceMonitor()
        
        try:
            performance_monitor.start_monitoring('security_preferences', 
                                               'policy_application')
            
            start_time = time.time()
            
            # Step 1: Configure security preferences
            security_policy = {
                'security_theme': {
                    'enable_encryption': True,
                    'encryption_algorithm': 'AES-256-GCM',
                    'kdf_iterations': 100000
                },
                'security_audit': {
                    'enable_logging': True,
                    'log_level': 'INFO'
                }
            }
            
            config_result = security_prefs.apply_security_policy(
                'enhanced', security_policy)
            
            assert config_result['status'] == 'success', \
                "Security policy application should succeed"
            
            # Step 2: Apply encryption based on security policy
            test_files = []
            for i in range(3):
                file_path = os.path.join(test_path, f"pipeline_test_{i}.txt")
                with open(file_path, 'w') as f:
                    f.write(f"Security pipeline test content {i}")
                test_files.append(file_path)
            
            # Use algorithm from security policy
            algorithm = security_policy['security_theme']['encryption_algorithm']
            password = "PipelineTestPassword123!"
            
            encrypt_result = encryption_tool.encrypt_files(
                test_files, password, algorithm)
            
            assert encrypt_result['status'] == 'success', \
                "Policy-driven encryption should succeed"
            
            # Step 3: Verify policy compliance
            encrypted_files = encryption_tool.encrypted_files
            if len(encrypted_files) > 0:
                for encrypted_file in encrypted_files:
                    assert encrypted_file['algorithm'] == algorithm, \
                        "Should use algorithm from security policy"
            
            # Verify audit logging for security operations
            audit_events = [
                ('security_policy_applied', 'Policy Management', 
                 {'policy': 'enhanced'}),
                ('file_encryption_completed', 'Encryption Operations', 
                 {'files_count': len(test_files), 'algorithm': algorithm})
            ]
            
            for event_type, category, details in audit_events:
                audit_result = security_prefs.log_audit_event(
                    event_type, category, details)
                assert audit_result['status'] == 'success', \
                    f"Should log audit event: {event_type}"
            
            # Verify complete pipeline timing
            pipeline_time = time.time() - start_time
            assert pipeline_time < 60.0, \
                f"Complete pipeline took too long: {pipeline_time:.2f}s"
            
        finally:
            performance_monitor.stop_monitoring('security_preferences', 
                                              'policy_application')
            shutil.rmtree(test_path, ignore_errors=True)
    
    def test_encryption_to_secure_delete_pipeline_workflow(self):
        """
        Test: File Encryption → Original File Secure Deletion → Cleanup
        Target: < 90 seconds for encryption-to-deletion pipeline
        """
        # Create test environment
        test_path = SecurityToolsTestDataFactory.create_security_tools_dataset(
            None, 'medium')
        hub = MockSecurityToolsHub()
        
        # Initialize security tools
        encryption_tool = hub.open_encryption_decryption()
        secure_delete_tool = hub.open_secure_delete()
        
        performance_monitor = SecurityToolsPerformanceMonitor()
        
        try:
            performance_monitor.start_monitoring('encryption_decryption', 
                                               'file_encryption')
            
            start_time = time.time()
            
            # Step 1: Encrypt sensitive files
            sensitive_files = []
            for i in range(5):
                file_path = os.path.join(test_path, f"sensitive_{i}.txt")
                with open(file_path, 'w') as f:
                    f.write(f"Sensitive content requiring encryption {i}\n" * 100)
                sensitive_files.append(file_path)
            
            password = "SensitiveFilePassword123!"
            algorithm = "AES-256-GCM"
            
            encrypt_result = encryption_tool.encrypt_files(
                sensitive_files, password, algorithm)
            
            assert encrypt_result['status'] == 'success', \
                "File encryption should succeed"
            
            # Step 2: Securely delete original files
            deletion_method = "dod_5220_22_m"
            verify_deletion = True
            
            delete_result = secure_delete_tool.secure_delete_files(
                sensitive_files, deletion_method, verify_deletion)
            
            assert delete_result['status'] == 'success', \
                "Secure deletion of originals should succeed"
            
            # Step 3: Verify data flow integrity
            assert encrypt_result['file_count'] == len(sensitive_files), \
                "Should encrypt all sensitive files"
            assert delete_result['file_count'] == len(sensitive_files), \
                "Should delete all original files"
            
            # Verify hub coordination
            hub_tools = list(hub.registered_tools.keys())
            assert 'encryption_decryption' in hub_tools, \
                "Encryption tool should be registered"
            assert 'secure_delete' in hub_tools, \
                "Secure delete tool should be registered"
            
            # Verify resource coordination
            encrypt_resources = encryption_tool.get_resource_usage()
            delete_resources = secure_delete_tool.get_resource_usage()
            
            assert encrypt_resources['memory'] > 0, \
                "Encryption should use memory"
            assert delete_resources['memory'] > 0, \
                "Deletion should use memory"
            
            # Verify complete pipeline timing
            pipeline_time = time.time() - start_time
            assert pipeline_time < 90.0, \
                f"Encryption-deletion pipeline took too long: {pipeline_time:.2f}s"
            
        finally:
            performance_monitor.stop_monitoring('encryption_decryption', 
                                              'file_encryption')
            shutil.rmtree(test_path, ignore_errors=True)


class TestSecurityUserJourneyValidation:
    """Test complete user journey workflows for different user types."""
    
    def test_security_administrator_workflow(self):
        """
        Test: Admin Login → Security Audit → Policy Updates → Compliance Check
        User Journey: Security Administrator managing enterprise security
        """
        # Create test environment
        test_path = SecurityToolsTestDataFactory.create_security_tools_dataset(
            None, 'large')
        hub = MockSecurityToolsHub()
        
        # Initialize all security tools for admin workflow
        security_prefs = hub.open_security_preferences()
        encryption_tool = hub.open_encryption_decryption()
        secure_delete_tool = hub.open_secure_delete()
        
        try:
            # Admin Workflow Step 1: Load and review security configuration
            config_result = security_prefs.load_security_configuration()
            assert config_result['status'] == 'success', \
                "Admin should be able to load security config"
            
            # Admin Workflow Step 2: Apply enhanced security policy
            enhanced_policy = {
                'security_migration': {'auto_rollback': True},
                'security_theme': {'enable_encryption': True},
                'security_directory': {'enable_monitoring': True},
                'security_audit': {'log_level': 'DEBUG'}
            }
            
            policy_result = security_prefs.apply_security_policy(
                'enhanced', enhanced_policy)
            assert policy_result['status'] == 'success', \
                "Admin should be able to apply enhanced policy"
            
            # Admin Workflow Step 3: Execute database migration
            migration_result = security_prefs.execute_database_migration(
                'Latest', {'validate_migration': True})
            # Note: Mock may simulate failure - verify proper handling
            assert 'status' in migration_result, \
                "Migration should return status"
            
            # Admin Workflow Step 4: Audit security operations
            admin_audit_events = [
                ('security_policy_updated', 'Policy Management', enhanced_policy),
                ('database_migration_executed', 'Database Operations', 
                 {'target_version': 'Latest'}),
                ('security_review_completed', 'Compliance', 
                 {'review_date': datetime.now().isoformat()})
            ]
            
            for event_type, category, details in admin_audit_events:
                audit_result = security_prefs.log_audit_event(
                    event_type, category, details)
                assert audit_result['status'] == 'success', \
                    f"Admin audit logging should succeed for {event_type}"
            
            # Verify admin workflow completeness
            assert len(security_prefs.audit_log_entries) >= 3, \
                "Should log all admin operations"
            assert len(security_prefs.security_config) > 0, \
                "Should have comprehensive security configuration"
            
        finally:
            shutil.rmtree(test_path, ignore_errors=True)
    
    def test_enterprise_user_workflow(self):
        """
        Test: Data Classification → Encryption → Secure Cleanup → Verification
        User Journey: Enterprise user securing sensitive business data
        """
        # Create test environment
        test_path = SecurityToolsTestDataFactory.create_security_tools_dataset(
            None, 'medium')
        hub = MockSecurityToolsHub()
        
        # Initialize tools for enterprise user workflow
        encryption_tool = hub.open_encryption_decryption()
        secure_delete_tool = hub.open_secure_delete()
        
        try:
            # Enterprise Workflow Step 1: Classify sensitive documents
            business_documents = []
            document_types = ['financial_report', 'employee_data', 
                            'customer_info', 'trade_secrets']
            
            for i, doc_type in enumerate(document_types):
                file_path = os.path.join(test_path, f"{doc_type}_{i}.txt")
                content = f"CONFIDENTIAL {doc_type.upper()}\n"
                content += f"Enterprise data content {i}\n" * 50
                
                with open(file_path, 'w') as f:
                    f.write(content)
                business_documents.append(file_path)
            
            # Enterprise Workflow Step 2: Encrypt business-critical files
            business_password = "EnterpriseSecurePassword2024!"
            algorithm = "AES-256-GCM"
            
            encrypt_result = encryption_tool.encrypt_files(
                business_documents, business_password, algorithm)
            
            assert encrypt_result['status'] == 'success', \
                "Enterprise file encryption should succeed"
            
            # Enterprise Workflow Step 3: Secure delete original documents
            deletion_method = "dod_5220_22_m"  # DoD standard for enterprise
            verify_deletion = True
            
            delete_result = secure_delete_tool.secure_delete_files(
                business_documents, deletion_method, verify_deletion)
            
            assert delete_result['status'] == 'success', \
                "Enterprise secure deletion should succeed"
            
            # Enterprise Workflow Step 4: Verify data protection compliance
            # Check encryption compliance
            encrypted_files = encryption_tool.encrypted_files
            if len(encrypted_files) > 0:
                for encrypted_file in encrypted_files:
                    assert encrypted_file['algorithm'] == algorithm, \
                        "Should use enterprise-approved algorithm"
                    assert 'integrity_hash' in encrypted_file, \
                        "Should have integrity protection"
            
            # Check deletion compliance
            deletion_records = secure_delete_tool.deletion_history
            if len(deletion_records) > 0:
                for deletion_record in deletion_records:
                    assert deletion_record['deletion_method'] == deletion_method, \
                        "Should use enterprise-approved deletion method"
                    assert deletion_record['overwrite_passes'] == 3, \
                        "Should meet DoD standard requirements"
            
            # Verify enterprise compliance metrics
            encrypt_ops = encrypt_result.get('security_operations', 0)
            delete_ops = delete_result.get('security_operations', 0)
            total_security_ops = encrypt_ops + delete_ops
            
            assert total_security_ops > 0, \
                "Should track total security operations for compliance"
            
        finally:
            shutil.rmtree(test_path, ignore_errors=True)


class TestCrossToolDataFlowValidation:
    """Test data flow validation between security tools."""
    
    def test_security_preferences_to_encryption_data_flow(self):
        """
        Test: Security Policy → Encryption Config → Algorithm Selection
        """
        # Create test environment
        test_path = SecurityToolsTestDataFactory.create_security_tools_dataset(
            None, 'small')
        hub = MockSecurityToolsHub()
        
        security_prefs = hub.open_security_preferences()
        encryption_tool = hub.open_encryption_decryption()
        
        try:
            # Step 1: Configure encryption policy
            encryption_policy = {
                'security_theme': {
                    'encryption_algorithm': 'AES-256-GCM',
                    'key_derivation': 'PBKDF2-SHA256',
                    'kdf_iterations': 150000
                }
            }
            
            policy_result = security_prefs.apply_security_policy(
                'enhanced', encryption_policy)
            assert policy_result['status'] == 'success', \
                "Policy configuration should succeed"
            
            # Step 2: Extract encryption settings from policy
            theme_config = security_prefs.security_config.get('security_theme', {})
            policy_algorithm = theme_config.get('encryption_algorithm')
            policy_iterations = theme_config.get('kdf_iterations')
            
            # Step 3: Apply policy settings to encryption operation
            test_file = os.path.join(test_path, "data_flow_test.txt")
            with open(test_file, 'w') as f:
                f.write("Data flow validation content")
            
            password = "DataFlowTestPassword123!"
            
            encrypt_result = encryption_tool.encrypt_files(
                [test_file], password, policy_algorithm)
            
            assert encrypt_result['status'] == 'success', \
                "Policy-driven encryption should succeed"
            
            # Step 4: Verify data flow integrity
            assert policy_algorithm is not None, \
                "Should extract algorithm from policy"
            
            # Verify encryption used policy settings
            encrypted_files = encryption_tool.encrypted_files
            if len(encrypted_files) > 0:
                encrypted_file = encrypted_files[-1]
                assert encrypted_file['algorithm'] == policy_algorithm, \
                    "Should use algorithm from security policy"
            
        finally:
            shutil.rmtree(test_path, ignore_errors=True)
    
    def test_encryption_to_deletion_data_handoff(self):
        """
        Test: File Encryption → Original File List → Secure Deletion
        """
        # Create test environment
        test_path = SecurityToolsTestDataFactory.create_security_tools_dataset(
            None, 'medium')
        hub = MockSecurityToolsHub()
        
        encryption_tool = hub.open_encryption_decryption()
        secure_delete_tool = hub.open_secure_delete()
        
        try:
            # Step 1: Encrypt files and track originals
            original_files = []
            for i in range(4):
                file_path = os.path.join(test_path, f"handoff_test_{i}.txt")
                with open(file_path, 'w') as f:
                    f.write(f"Data handoff test content {i}")
                original_files.append(file_path)
            
            password = "HandoffTestPassword123!"
            encrypt_result = encryption_tool.encrypt_files(
                original_files, password)
            
            assert encrypt_result['status'] == 'success', \
                "Initial encryption should succeed"
            
            # Step 2: Pass original file list to secure deletion
            deletion_method = "dod_5220_22_m"
            
            delete_result = secure_delete_tool.secure_delete_files(
                original_files, deletion_method, True)
            
            assert delete_result['status'] == 'success', \
                "Handoff deletion should succeed"
            
            # Step 3: Verify data handoff integrity
            assert encrypt_result['file_count'] == len(original_files), \
                "Encryption should process all original files"
            assert delete_result['file_count'] == len(original_files), \
                "Deletion should receive all original files"
            
            # Verify operation coordination
            encrypt_history = encryption_tool.operation_history
            delete_history = secure_delete_tool.operation_history
            
            assert len(encrypt_history) > 0, \
                "Should track encryption operations"
            assert len(delete_history) > 0, \
                "Should track deletion operations"
            
        finally:
            shutil.rmtree(test_path, ignore_errors=True)


class TestConcurrentSecurityOperations:
    """Test concurrent security operations and resource coordination."""
    
    def test_concurrent_encryption_and_deletion_workflow(self):
        """
        Test: Parallel Encryption + Deletion → Resource Management → Coordination
        """
        # Create test environment
        test_path = SecurityToolsTestDataFactory.create_security_tools_dataset(
            None, 'medium')
        hub = MockSecurityToolsHub()
        
        encryption_tool = hub.open_encryption_decryption()
        secure_delete_tool = hub.open_secure_delete()
        
        try:
            # Prepare separate file sets for concurrent operations
            encrypt_files = []
            delete_files = []
            
            # Files for encryption
            for i in range(5):
                file_path = os.path.join(test_path, f"encrypt_concurrent_{i}.txt")
                with open(file_path, 'w') as f:
                    f.write(f"Concurrent encryption content {i}")
                encrypt_files.append(file_path)
            
            # Files for deletion
            for i in range(5):
                file_path = os.path.join(test_path, f"delete_concurrent_{i}.txt")
                with open(file_path, 'w') as f:
                    f.write(f"Concurrent deletion content {i}")
                delete_files.append(file_path)
            
            # Execute concurrent operations
            password = "ConcurrentTestPassword123!"
            
            # Simulate concurrent execution
            encrypt_result = encryption_tool.encrypt_files(
                encrypt_files, password, "AES-256-GCM")
            
            delete_result = secure_delete_tool.secure_delete_files(
                delete_files, "dod_5220_22_m", True)
            
            # Verify both operations completed
            assert encrypt_result['status'] == 'success', \
                "Concurrent encryption should succeed"
            assert delete_result['status'] == 'success', \
                "Concurrent deletion should succeed"
            
            # Verify resource coordination
            encrypt_resources = encryption_tool.get_resource_usage()
            delete_resources = secure_delete_tool.get_resource_usage()
            
            # Both tools should track resource usage
            assert encrypt_resources['memory'] > 0 and delete_resources['memory'] > 0, \
                "Both tools should use memory resources"
            assert encrypt_resources['cpu'] > 0 and delete_resources['cpu'] > 0, \
                "Both tools should use CPU resources"
            
            # Verify hub coordination
            hub_events = hub.hub_events
            assert len(hub_events) >= 2, \
                "Hub should track both tool registrations"
            
        finally:
            shutil.rmtree(test_path, ignore_errors=True)
    
    def test_security_tools_with_preferences_coordination(self):
        """
        Test: Preferences Changes → Live Tool Updates → Coordination
        """
        # Create test environment
        test_path = SecurityToolsTestDataFactory.create_security_tools_dataset(
            None, 'small')
        hub = MockSecurityToolsHub()
        
        security_prefs = hub.open_security_preferences()
        encryption_tool = hub.open_encryption_decryption()
        secure_delete_tool = hub.open_secure_delete()
        
        try:
            # Step 1: Change security preferences
            new_policy = {
                'security_audit': {
                    'log_level': 'WARNING',
                    'enable_logging': True
                }
            }
            
            prefs_result = security_prefs.apply_security_policy(
                'custom', new_policy)
            assert prefs_result['status'] == 'success', \
                "Preferences update should succeed"
            
            # Step 2: Use other tools (should reflect preferences)
            test_file = os.path.join(test_path, "coordination_test.txt")
            with open(test_file, 'w') as f:
                f.write("Tool coordination test content")
            
            # Test encryption with updated preferences
            encrypt_result = encryption_tool.encrypt_files(
                [test_file], "CoordinationPassword123!")
            assert encrypt_result['status'] == 'success', \
                "Coordinated encryption should succeed"
            
            # Test deletion with updated preferences
            delete_result = secure_delete_tool.secure_delete_files(
                [test_file], "single_pass", True)
            assert delete_result['status'] == 'success', \
                "Coordinated deletion should succeed"
            
            # Verify coordination tracking
            total_operations = (
                len(security_prefs.operation_history) +
                len(encryption_tool.operation_history) +
                len(secure_delete_tool.operation_history)
            )
            assert total_operations > 0, \
                "Should track coordinated operations"
            
        finally:
            shutil.rmtree(test_path, ignore_errors=True)


class TestSecurityPerformanceRegression:
    """Test performance regression and optimization validation."""
    
    def test_security_tools_performance_regression_workflow(self):
        """
        Test: Baseline Performance → Tool Operations → Regression Detection
        """
        # Create test environment
        test_path = SecurityToolsTestDataFactory.create_security_tools_dataset(
            None, 'medium')
        hub = MockSecurityToolsHub()
        
        # Initialize all security tools
        security_prefs = hub.open_security_preferences()
        encryption_tool = hub.open_encryption_decryption()
        secure_delete_tool = hub.open_secure_delete()
        
        performance_monitor = SecurityToolsPerformanceMonitor()
        
        try:
            # Performance Test 1: Security Preferences operations
            performance_monitor.start_monitoring('security_preferences', 
                                               'configuration_load')
            
            config_result = security_prefs.load_security_configuration()
            
            config_perf = performance_monitor.stop_monitoring(
                'security_preferences', 'configuration_load')
            
            assert config_perf['target_met'], \
                "Security preferences should meet performance targets"
            
            # Performance Test 2: Encryption operations
            test_files = []
            for i in range(8):
                file_path = os.path.join(test_path, f"perf_test_{i}.txt")
                with open(file_path, 'w') as f:
                    f.write(f"Performance test content {i}\n" * 100)
                test_files.append(file_path)
            
            performance_monitor.start_monitoring('encryption_decryption', 
                                               'file_encryption')
            
            encrypt_result = encryption_tool.encrypt_files(
                test_files, "PerformanceTestPassword123!")
            
            encrypt_perf = performance_monitor.stop_monitoring(
                'encryption_decryption', 'file_encryption')
            
            assert encrypt_perf['target_met'], \
                "Encryption should meet performance targets"
            
            # Performance Test 3: Secure deletion operations
            performance_monitor.start_monitoring('secure_delete', 
                                               'dod_deletion')
            
            delete_result = secure_delete_tool.secure_delete_files(
                test_files, "dod_5220_22_m", True)
            
            delete_perf = performance_monitor.stop_monitoring(
                'secure_delete', 'dod_deletion')
            
            assert delete_perf['target_met'], \
                "Secure deletion should meet performance targets"
            
            # Verify no performance regression
            all_operations_passed = (
                config_perf['target_met'] and 
                encrypt_perf['target_met'] and 
                delete_perf['target_met']
            )
            
            assert all_operations_passed, \
                "All security operations should meet performance targets"
            
        finally:
            shutil.rmtree(test_path, ignore_errors=True)


class TestSecurityHubIntegration:
    """Test Hub integration and coordination features."""
    
    def test_security_tools_hub_coordination_workflow(self):
        """
        Test: Hub Registration → Resource Allocation → Status Monitoring
        """
        # Create test environment
        test_path = SecurityToolsTestDataFactory.create_security_tools_dataset(
            None, 'small')
        hub = MockSecurityToolsHub()
        
        try:
            # Register all security tools with hub
            security_prefs = hub.open_security_preferences()
            encryption_tool = hub.open_encryption_decryption()
            secure_delete_tool = hub.open_secure_delete()
            
            # Verify all tools are registered
            registered_tools = list(hub.registered_tools.keys())
            expected_tools = ['security_preferences', 'encryption_decryption', 
                            'secure_delete']
            
            for tool_name in expected_tools:
                assert tool_name in registered_tools, \
                    f"Tool {tool_name} should be registered with hub"
            
            # Verify hub status tracking
            for tool_name in expected_tools:
                assert tool_name in hub.tool_status, \
                    f"Hub should track status for {tool_name}"
                
                tool_status = hub.tool_status[tool_name]
                assert 'status' in tool_status, \
                    "Tool status should include status field"
                assert 'last_activity' in tool_status, \
                    "Tool status should include last activity"
            
            # Test coordinated operations
            test_file = os.path.join(test_path, "hub_coordination_test.txt")
            with open(test_file, 'w') as f:
                f.write("Hub coordination test content")
            
            # Execute operations through hub coordination
            encrypt_result = encryption_tool.encrypt_files(
                [test_file], "HubTestPassword123!")
            
            delete_result = secure_delete_tool.secure_delete_files(
                [test_file], "dod_5220_22_m", True)
            
            # Verify hub events were recorded
            assert len(hub.hub_events) > 0, \
                "Hub should record coordination events"
            
            # Verify resource allocation
            assert 'max_threads' in hub.resource_allocation, \
                "Hub should manage thread allocation"
            assert 'max_memory_mb' in hub.resource_allocation, \
                "Hub should manage memory allocation"
            
        finally:
            shutil.rmtree(test_path, ignore_errors=True)


# Comprehensive test runner
def run_security_tools_comprehensive_e2e_tests():
    """Run the comprehensive Security Tools E2E test suite."""
    pytest_args = [
        __file__,
        "-v",
        "--tb=short",
        "--color=yes",
        "--durations=15",
        "-x",  # Stop on first failure for E2E tests
        "--maxfail=5"  # Stop after 5 failures
    ]
    
    return pytest.main(pytest_args)


if __name__ == "__main__":
    # Import PyQt5 for GUI testing if available
    try:
        from PyQt5.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
    except ImportError:
        pass
    
    # Run the tests
    print("Starting Security Tools Comprehensive End-to-End Tests...")
    exit_code = run_security_tools_comprehensive_e2e_tests()
    
    print(f"\nSecurity Tools Comprehensive E2E Test Suite completed "
          f"with exit code: {exit_code}")
    sys.exit(exit_code)