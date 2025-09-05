#!/usr/bin/env python3
"""
Privacy Cleaner End-to-End Test Suite

Comprehensive E2E testing for Privacy Cleaner functionality.
Tests data identification workflows, selective cleaning operations,
privacy assessment capabilities, and compliance verification processes.

Created: 2025-09-05
Coverage: Privacy Cleaner data identification, selective cleaning,
          privacy assessment, and compliance verification workflows
Priority: HIGH (addressing 0% E2E coverage for Privacy Tools)
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
    from tests.e2e.privacy_tools_test_utilities import (
        MockPrivacyCleanerTool, MockPrivacyToolsHub,
        PrivacyToolsPerformanceMonitor, PrivacyToolsSignalTracker,
        PrivacyToolsTestDataFactory, assert_performance_target,
        create_test_sensitive_data, privacy_cleaner_test_environment)
    UTILITIES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import utilities: {e}")
    UTILITIES_AVAILABLE = False

# Skip all tests if utilities not available
pytestmark = pytest.mark.skipif(
    not UTILITIES_AVAILABLE, 
    reason="Privacy Tools utilities not available"
)


class TestPrivacyCleanerDataIdentification:
    """End-to-end testing of Privacy Cleaner data identification workflows."""
    
    def test_multi_format_data_identification_workflow(self, 
                                                      privacy_cleaner_test_environment):
        """
        Test: Multi-Format Scanning → Pattern Detection → Risk Assessment → Results
        Target: < 30 seconds for 100 files
        """
        env = privacy_cleaner_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        signal_tracker = env['signal_tracker']
        
        # Connect signal tracking
        signal_tracker.connect_all_signals()
        
        # Start performance monitoring
        performance_monitor.start_monitoring('privacy_cleaner', 
                                           'multi_format_scan')
        
        start_time = time.time()
        
        try:
            # Create test files with sensitive data
            test_files = []
            for i in range(20):
                file_path = os.path.join(test_data_path, f"sensitive_doc_{i}.txt")
                content = f"Document {i}\nEmployee: John Doe\nSSN: 123-45-{i:04d}\nEmail: john.doe{i}@company.com\n"
                with open(file_path, 'w') as f:
                    f.write(content)
                test_files.append(file_path)
            
            # Execute multi-format data identification workflow
            detection_config = {
                'data_types': ['pii', 'phi', 'financial'],
                'algorithms': ['regex', 'context_analysis'],
                'confidence_threshold': 0.8
            }
            
            result = tool.scan_for_sensitive_data(test_files, detection_config)
            
            # Verify data identification completion
            assert result is not None, "Scan result should not be None"
            assert result['status'] == 'success', \
                f"Data identification should succeed, got: {result.get('status')}"
            assert 'sensitive_data_detected' in result, \
                "Result should include sensitive data count"
            assert result['sensitive_data_detected'] > 0, \
                "Should detect sensitive data patterns"
            
            # Verify scan covered all files
            assert result['files_processed'] == len(test_files), \
                f"Should process all {len(test_files)} files"
            
            # Verify sensitive data was detected and stored
            assert len(tool.detected_sensitive_data) > 0, \
                "Tool should have detected sensitive data"
            
            # Verify workflow timing
            workflow_time = time.time() - start_time
            assert workflow_time < 30.0, \
                f"Multi-format scan took too long: {workflow_time:.2f}s"
            
            # Validate signal progression
            workflow_summary = signal_tracker.get_workflow_summary()
            assert workflow_summary['completion_status'], \
                "Workflow should complete successfully"
            assert workflow_summary['total_events'] > 0, \
                "Should have workflow events"
            
        finally:
            # Stop performance monitoring
            perf_result = performance_monitor.stop_monitoring(
                'privacy_cleaner', 'multi_format_scan')
            assert perf_result['target_met'], \
                f"Performance target not met: {perf_result}"
    
    def test_pii_pattern_detection_workflow(self, 
                                          privacy_cleaner_test_environment):
        """
        Test: PII Pattern Recognition → Validation → Context Analysis → Categorization
        Target: < 25 seconds for PII pattern analysis
        """
        env = privacy_cleaner_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        
        performance_monitor.start_monitoring('privacy_cleaner', 
                                           'pii_pattern_detection')
        
        start_time = time.time()
        
        try:
            # Create test files with specific PII patterns
            pii_test_data = [
                ("ssn_file.txt", "Employee SSN: 123-45-6789\nEmployee ID: EMP001"),
                ("email_file.txt", "Contact: john.doe@example.com\nBackup: jane.smith@company.org"),
                ("phone_file.txt", "Primary: (555) 123-4567\nSecondary: +1-800-555-0199"),
                ("credit_file.txt", "Card Number: 4111-1111-1111-1111\nExpiry: 12/25"),
                ("address_file.txt", "Address: 123 Main St, Anytown, ST 12345\nZip: 12345")
            ]
            
            test_files = []
            for filename, content in pii_test_data:
                file_path = os.path.join(test_data_path, filename)
                with open(file_path, 'w') as f:
                    f.write(content)
                test_files.append(file_path)
            
            # Test PII pattern detection
            detection_config = {
                'data_types': ['pii'],
                'patterns': ['ssn', 'email', 'phone', 'credit_card', 'address'],
                'confidence_threshold': 0.8
            }
            
            result = tool.scan_for_sensitive_data(test_files, detection_config)
            
            # Verify PII detection results
            assert result['status'] == 'success', \
                "PII pattern detection should succeed"
            assert result['sensitive_data_detected'] >= len(pii_test_data), \
                f"Should detect at least {len(pii_test_data)} PII patterns"
            
            # Verify detection covered all test files
            assert result['files_processed'] == len(test_files), \
                "Should process all PII test files"
            
            # Verify sensitive data storage
            for file_path in test_files:
                if file_path in tool.detected_sensitive_data:
                    detection_data = tool.detected_sensitive_data[file_path]
                    assert 'patterns' in detection_data, \
                        "Detection data should include patterns"
                    assert len(detection_data['patterns']) > 0, \
                        "Should detect patterns in sensitive files"
            
            workflow_time = time.time() - start_time
            assert workflow_time < 25.0, \
                f"PII detection took too long: {workflow_time:.2f}s"
                
        finally:
            performance_monitor.stop_monitoring('privacy_cleaner', 
                                              'pii_pattern_detection')


class TestPrivacyCleanerComplianceVerification:
    """Test regulatory compliance frameworks and verification."""
    
    def test_gdpr_compliance_validation_workflow(self, 
                                               privacy_cleaner_test_environment):
        """
        Test: GDPR Article 17 → Right to Erasure → Complete Deletion → Audit Trail
        Target: < 15 seconds for GDPR compliance validation
        """
        env = privacy_cleaner_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        signal_tracker = env['signal_tracker']
        
        signal_tracker.connect_all_signals()
        performance_monitor.start_monitoring('privacy_cleaner', 
                                           'gdpr_validation')
        
        start_time = time.time()
        
        try:
            # Create test data for GDPR compliance testing
            gdpr_test_files = []
            for i in range(5):
                file_path = os.path.join(test_data_path, f"gdpr_test_{i}.txt")
                content = f"GDPR Test Document {i}\nName: EU Citizen {i}\nEmail: citizen{i}@example.eu\n"
                with open(file_path, 'w') as f:
                    f.write(content)
                gdpr_test_files.append(file_path)
            
            # Scan for GDPR-relevant data
            detection_config = {
                'data_types': ['pii'],
                'regulatory_context': 'gdpr',
                'data_subject_rights': True
            }
            
            scan_result = tool.scan_for_sensitive_data(gdpr_test_files, detection_config)
            
            # Verify GDPR compliance
            compliance_result = tool.verify_compliance(
                'gdpr', {'cleaned_files': gdpr_test_files, 'method': 'erasure'})
            
            # Verify GDPR compliance validation
            assert scan_result['status'] == 'success', \
                "GDPR data scan should succeed"
            assert compliance_result['status'] == 'success', \
                "GDPR compliance verification should succeed"
            
            # Verify GDPR-specific compliance
            if 'gdpr' in tool.compliance_status:
                gdpr_status = tool.compliance_status['gdpr']
                assert gdpr_status['validation_passed'], \
                    "GDPR compliance validation should pass"
                assert 'requirements_met' in gdpr_status, \
                    "Should verify GDPR requirements"
            
            workflow_time = time.time() - start_time
            assert workflow_time < 15.0, \
                f"GDPR compliance validation took too long: {workflow_time:.2f}s"
            
        finally:
            perf_result = performance_monitor.stop_monitoring(
                'privacy_cleaner', 'gdpr_validation')
            assert perf_result['target_met'], \
                f"GDPR validation performance target not met: {perf_result}"


class TestPrivacyCleanerIntegration:
    """Test integration between Privacy Cleaner and other components."""
    
    def test_privacy_cleaner_hub_integration_workflow(self, 
                                                    privacy_cleaner_test_environment):
        """
        Test: Privacy Config → Hub Registration → Cross-tool Communication
        """
        env = privacy_cleaner_test_environment
        privacy_tool = env['tool']
        hub = env['hub']
        
        # Verify tool is registered with hub
        assert 'privacy_cleaner' in hub.registered_tools, \
            "Privacy Cleaner should be registered with hub"
        
        # Verify hub coordination
        hub_status = hub.tool_status
        assert 'privacy_cleaner' in hub_status, \
            "Hub should track Privacy Cleaner status"
        
        # Test configuration change notification
        detection_config = {'data_types': ['pii'], 'algorithms': ['regex']}
        
        result = privacy_tool.scan_for_sensitive_data([], detection_config)
        
        assert result['status'] == 'success', \
            "Hub-integrated scanning should succeed"
        
        # Verify resource coordination
        resource_usage = privacy_tool.get_resource_usage()
        assert isinstance(resource_usage, dict), \
            "Should track resource usage for hub coordination"
        assert 'memory' in resource_usage, "Should track memory usage"
        assert 'cpu' in resource_usage, "Should track CPU usage"


# Test runner configuration
def run_privacy_cleaner_e2e_tests():
    """Run the Privacy Cleaner E2E test suite."""
    pytest_args = [
        __file__,
        "-v",
        "--tb=short",
        "--color=yes",
        "--durations=10",
        "-x",  # Stop on first failure for E2E tests
        "--maxfail=3"  # Stop after 3 failures
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
    print("Starting Privacy Cleaner End-to-End Tests...")
    exit_code = run_privacy_cleaner_e2e_tests()
    
    print(f"\nPrivacy Cleaner E2E Test Suite completed "
          f"with exit code: {exit_code}")
    sys.exit(exit_code)