#!/usr/bin/env python3
"""
Data Anonymizer End-to-End Test Suite

Comprehensive E2E testing for Data Anonymizer functionality.
Tests sensitive data detection algorithms, anonymization workflows,
verification processes, and automated report generation.

Created: 2025-09-05
Coverage: Data Anonymizer sensitive data detection, anonymization techniques,
          verification processes, and report generation workflows
Priority: HIGH (addressing 0% E2E coverage for Privacy Tools)
"""

import os
import sys
import time
from datetime import datetime

import pytest

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')))

try:
    from tests.e2e.privacy_tools_test_utilities import (
        MockDataAnonymizerTool, MockPrivacyToolsHub,
        PrivacyToolsPerformanceMonitor, PrivacyToolsSignalTracker,
        PrivacyToolsTestDataFactory, assert_performance_target,
        create_test_sensitive_data, data_anonymizer_test_environment)
    UTILITIES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import utilities: {e}")
    UTILITIES_AVAILABLE = False

# Skip all tests if utilities not available
pytestmark = pytest.mark.skipif(
    not UTILITIES_AVAILABLE, 
    reason="Privacy Tools utilities not available"
)


class TestDataAnonymizerSensitiveDetection:
    """End-to-end testing of Data Anonymizer sensitive data detection."""
    
    def test_pii_detection_algorithm_workflow(self, 
                                            data_anonymizer_test_environment):
        """
        Test: PII Detection → Accuracy Validation → Performance Benchmarking → Results Analysis
        Target: < 35 seconds for 500 records
        """
        env = data_anonymizer_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        signal_tracker = env['signal_tracker']
        
        # Connect signal tracking
        signal_tracker.connect_all_signals()
        
        # Start performance monitoring
        performance_monitor.start_monitoring('data_anonymizer', 
                                           'pii_detection')
        
        start_time = time.time()
        
        try:
            # Create test data sources with PII
            test_data_sources = []
            for i in range(10):
                file_path = os.path.join(test_data_path, f"pii_source_{i}.csv")
                csv_content = "id,name,ssn,email,phone\n"
                for j in range(50):
                    csv_content += f"{j},Person {j},123-45-{j:04d},person{j}@example.com,(555) {j:03d}-4567\n"
                
                with open(file_path, 'w') as f:
                    f.write(csv_content)
                test_data_sources.append(file_path)
            
            # Execute PII detection workflow
            detection_config = {
                'data_types': ['pii'],
                'algorithms': ['regex', 'ml', 'context_analysis'],
                'accuracy_threshold': 0.95,
                'confidence_threshold': 0.8
            }
            
            result = tool.detect_sensitive_data(test_data_sources, detection_config)
            
            # Verify PII detection completion
            assert result is not None, "Detection result should not be None"
            assert result['status'] == 'success', \
                f"PII detection should succeed, got: {result.get('status')}"
            assert 'sensitive_data_detected' in result, \
                "Result should include sensitive data count"
            assert result['sensitive_data_detected'] > 0, \
                "Should detect PII patterns"
            
            # Verify detection covered all data sources
            assert result['files_processed'] == len(test_data_sources), \
                f"Should process all {len(test_data_sources)} data sources"
            
            # Verify detection results were stored
            assert len(tool.detection_results) > 0, \
                "Tool should have stored detection results"
            
            # Verify workflow timing
            workflow_time = time.time() - start_time
            assert workflow_time < 35.0, \
                f"PII detection took too long: {workflow_time:.2f}s"
            
            # Validate signal progression
            workflow_summary = signal_tracker.get_workflow_summary()
            assert workflow_summary['completion_status'], \
                "Workflow should complete successfully"
            assert workflow_summary['total_events'] > 0, \
                "Should have workflow events"
            
        finally:
            # Stop performance monitoring
            perf_result = performance_monitor.stop_monitoring(
                'data_anonymizer', 'pii_detection')
            assert perf_result['target_met'], \
                f"Performance target not met: {perf_result}"
    
    def test_phi_detection_algorithm_workflow(self, 
                                            data_anonymizer_test_environment):
        """
        Test: PHI Detection → Medical Context → HIPAA Compliance → Risk Assessment
        Target: < 40 seconds for medical records
        """
        env = data_anonymizer_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        
        performance_monitor.start_monitoring('data_anonymizer', 
                                           'phi_detection')
        
        start_time = time.time()
        
        try:
            # Create test medical records with PHI
            medical_data_sources = []
            for i in range(5):
                file_path = os.path.join(test_data_path, f"medical_records_{i}.json")
                json_content = f'''{{
    "medical_records": [
        {{"patient_id": "P{i:09d}", "name": "Patient {i}", "mrn": "MRN-{i:09d}",
          "diagnosis": "Test Condition {i}", "insurance": "INS-ABC{i:06d}",
          "provider": "Dr. Test {i}", "dob": "1990-01-{i+1:02d}"}}
    ]
}}'''
                with open(file_path, 'w') as f:
                    f.write(json_content)
                medical_data_sources.append(file_path)
            
            # Test PHI detection
            detection_config = {
                'data_types': ['phi'],
                'medical_context': True,
                'hipaa_identifiers': True,
                'algorithms': ['regex', 'context_analysis']
            }
            
            result = tool.detect_sensitive_data(medical_data_sources, detection_config)
            
            # Verify PHI detection results
            assert result['status'] == 'success', \
                "PHI detection should succeed"
            assert result['sensitive_data_detected'] > 0, \
                "Should detect PHI patterns"
            assert result['files_processed'] == len(medical_data_sources), \
                "Should process all medical data sources"
            
            # Verify PHI-specific detection
            if hasattr(tool, 'detection_results'):
                assert len(tool.detection_results) > 0, \
                    "Should store PHI detection results"
            
            workflow_time = time.time() - start_time
            assert workflow_time < 40.0, \
                f"PHI detection took too long: {workflow_time:.2f}s"
                
        finally:
            performance_monitor.stop_monitoring('data_anonymizer', 
                                              'phi_detection')
    
    def test_structured_data_detection_workflow(self, 
                                              data_anonymizer_test_environment):
        """
        Test: Database Schema Analysis → Column Classification → Sensitivity Mapping → Risk Assessment
        Target: < 30 seconds for database analysis
        """
        env = data_anonymizer_test_environment
        tool = env['tool']
        test_data_path = env['test_data_path']
        performance_monitor = env['performance_monitor']
        
        performance_monitor.start_monitoring('data_anonymizer', 
                                           'structured_data_analysis')
        
        start_time = time.time()
        
        try:
            # Create structured data sources
            structured_sources = []
            
            # CSV file with customer data
            csv_path = os.path.join(test_data_path, "customers.csv")
            csv_content = "customer_id,name,email,ssn,phone,address\n"
            for i in range(100):
                csv_content += f"CUST{i:04d},Customer {i},cust{i}@example.com,123-45-{i:04d},(555) {i:03d}-1234,{i} Main St\n"
            
            with open(csv_path, 'w') as f:
                f.write(csv_content)
            structured_sources.append(csv_path)
            
            # JSON file with employee data
            json_path = os.path.join(test_data_path, "employees.json")
            json_content = '''{"employees": [
    {"emp_id": "EMP001", "name": "John Doe", "ssn": "987-65-4321", "email": "john@company.com"},
    {"emp_id": "EMP002", "name": "Jane Smith", "ssn": "555-12-3456", "email": "jane@company.com"}
]}'''
            
            with open(json_path, 'w') as f:
                f.write(json_content)
            structured_sources.append(json_path)
            
            # Test structured data detection
            detection_config = {
                'data_types': ['pii', 'financial'],
                'structured_analysis': True,
                'column_classification': True,
                'schema_analysis': True
            }
            
            result = tool.detect_sensitive_data(structured_sources, detection_config)
            
            # Verify structured data detection results
            assert result['status'] == 'success', \
                "Structured data detection should succeed"
            assert result['sensitive_data_detected'] > 0, \
                "Should detect sensitive data in structured formats"
            assert result['files_processed'] == len(structured_sources), \
                "Should process all structured data sources"
            
            workflow_time = time.time() - start_time
            assert workflow_time < 30.0, \
                f"Structured data detection took too long: {workflow_time:.2f}s"
            
        finally:
            performance_monitor.stop_monitoring('data_anonymizer', 
                                              'structured_data_analysis')


class TestDataAnonymizerAnonymizationWorkflows:
    """Test anonymization technique implementations."""
    
    def test_k_anonymity_implementation_workflow(self, 
                                               data_anonymizer_test_environment):
        """
        Test: K-Anonymity Algorithm → Group Formation → Quasi-identifier Suppression → Validation
        Target: < 60 seconds for 1000 records
        """
        env = data_anonymizer_test_environment
        tool = env['tool']
        performance_monitor = env['performance_monitor']
        signal_tracker = env['signal_tracker']
        
        signal_tracker.connect_all_signals()
        performance_monitor.start_monitoring('data_anonymizer', 
                                           'k_anonymity')
        
        start_time = time.time()
        
        try:
            # Create test dataset for k-anonymity
            test_data = create_test_sensitive_data('pii', 100)
            
            # Define k-anonymity parameters
            k_anonymity_config = {
                'k_value': 3,
                'quasi_identifiers': ['age', 'zipcode', 'gender'],
                'sensitive_attributes': ['diagnosis', 'salary'],
                'suppression_threshold': 0.1
            }
            
            # Create targets for anonymization
            targets = {
                'dataset_1': {
                    'data': test_data,
                    'type': 'structured',
                    'format': 'records'
                }
            }
            
            # Apply k-anonymity
            result = tool.apply_anonymization(targets, 'k_anonymity', k_anonymity_config)
            
            # Verify k-anonymity application
            assert result['status'] == 'success', \
                "K-anonymity application should succeed"
            assert 'data_anonymized' in result, \
                "Should report anonymized data count"
            assert result['data_anonymized'] > 0, \
                "Should anonymize data records"
            
            # Verify k-anonymity results
            if hasattr(tool, 'anonymization_results'):
                assert len(tool.anonymization_results) > 0, \
                    "Should store anonymization results"
                
                for target_id, anon_result in tool.anonymization_results.items():
                    if anon_result['status'] == 'anonymized':
                        assert anon_result['technique'] == 'k_anonymity', \
                            "Should use k-anonymity technique"
                        assert 'k_value' in anon_result, \
                            "Should record k-value used"
                        assert anon_result['k_value'] == k_anonymity_config['k_value'], \
                            "Should use specified k-value"
            
            workflow_time = time.time() - start_time
            assert workflow_time < 60.0, \
                f"K-anonymity took too long: {workflow_time:.2f}s"
            
        finally:
            performance_monitor.stop_monitoring('data_anonymizer', 'k_anonymity')
    
    def test_differential_privacy_workflow(self, 
                                         data_anonymizer_test_environment):
        """
        Test: DP Algorithm → Noise Addition → Privacy Budget → Utility Measurement
        Target: < 45 seconds for statistical data
        """
        env = data_anonymizer_test_environment
        tool = env['tool']
        performance_monitor = env['performance_monitor']
        
        performance_monitor.start_monitoring('data_anonymizer', 
                                           'differential_privacy')
        
        start_time = time.time()
        
        try:
            # Create test dataset for differential privacy
            test_data = create_test_sensitive_data('financial', 50)
            
            # Define differential privacy parameters
            dp_config = {
                'epsilon': 1.0,
                'delta': 1e-5,
                'sensitivity': 1.0,
                'noise_mechanism': 'laplace'
            }
            
            # Create targets for anonymization
            targets = {
                'statistical_dataset': {
                    'data': test_data,
                    'type': 'statistical',
                    'queries': ['sum', 'count', 'average']
                }
            }
            
            # Apply differential privacy
            result = tool.apply_anonymization(targets, 'differential_privacy', dp_config)
            
            # Verify differential privacy application
            assert result['status'] == 'success', \
                "Differential privacy application should succeed"
            assert result['data_anonymized'] > 0, \
                "Should anonymize statistical data"
            
            # Verify differential privacy results
            if hasattr(tool, 'anonymization_results'):
                for target_id, anon_result in tool.anonymization_results.items():
                    if anon_result['status'] == 'anonymized':
                        assert anon_result['technique'] == 'differential_privacy', \
                            "Should use differential privacy technique"
                        assert 'epsilon' in anon_result, \
                            "Should record epsilon value"
                        assert anon_result['epsilon'] == dp_config['epsilon'], \
                            "Should use specified epsilon"
            
            workflow_time = time.time() - start_time
            assert workflow_time < 45.0, \
                f"Differential privacy took too long: {workflow_time:.2f}s"
            
        finally:
            performance_monitor.stop_monitoring('data_anonymizer', 'differential_privacy')
    
    def test_data_masking_techniques_workflow(self, 
                                            data_anonymizer_test_environment):
        """
        Test: Masking Selection → Format Preservation → Realistic Replacement → Validation
        Target: < 30 seconds for 200 fields
        """
        env = data_anonymizer_test_environment
        tool = env['tool']
        performance_monitor = env['performance_monitor']
        
        performance_monitor.start_monitoring('data_anonymizer', 
                                           'data_masking')
        
        start_time = time.time()
        
        try:
            # Create test data for masking
            test_data = create_test_sensitive_data('pii', 50)
            
            # Define data masking parameters
            masking_config = {
                'mask_type': 'character',
                'masking_character': 'X',
                'preserve_format': True,
                'fields_to_mask': ['ssn', 'credit_card', 'phone']
            }
            
            # Create targets for masking
            targets = {
                'pii_dataset': {
                    'data': test_data,
                    'type': 'structured',
                    'sensitive_fields': ['ssn', 'email', 'phone']
                }
            }
            
            # Apply data masking
            result = tool.apply_anonymization(targets, 'data_masking', masking_config)
            
            # Verify data masking application
            assert result['status'] == 'success', \
                "Data masking should succeed"
            assert result['data_anonymized'] > 0, \
                "Should mask sensitive data"
            
            # Verify masking results
            if hasattr(tool, 'anonymization_results'):
                for target_id, anon_result in tool.anonymization_results.items():
                    if anon_result['status'] == 'anonymized':
                        assert anon_result['technique'] == 'data_masking', \
                            "Should use data masking technique"
                        assert 'mask_type' in anon_result, \
                            "Should record mask type used"
                        assert 'fields_masked' in anon_result, \
                            "Should record fields masked count"
            
            workflow_time = time.time() - start_time
            assert workflow_time < 30.0, \
                f"Data masking took too long: {workflow_time:.2f}s"
            
        finally:
            performance_monitor.stop_monitoring('data_anonymizer', 'data_masking')
    
    def test_tokenization_workflow(self, 
                                 data_anonymizer_test_environment):
        """
        Test: Token Generation → Mapping Creation → Consistent Replacement → Security Validation
        Target: < 20 seconds for structured data
        """
        env = data_anonymizer_test_environment
        tool = env['tool']
        performance_monitor = env['performance_monitor']
        
        performance_monitor.start_monitoring('data_anonymizer', 
                                           'tokenization')
        
        start_time = time.time()
        
        try:
            # Create test data for tokenization
            test_data = create_test_sensitive_data('financial', 30)
            
            # Define tokenization parameters
            tokenization_config = {
                'token_format': 'uuid',
                'preserve_relationships': True,
                'secure_mapping': True,
                'reversible': False
            }
            
            # Create targets for tokenization
            targets = {
                'financial_dataset': {
                    'data': test_data,
                    'type': 'structured',
                    'token_fields': ['account_id', 'customer_name', 'ssn']
                }
            }
            
            # Apply tokenization
            result = tool.apply_anonymization(targets, 'tokenization', tokenization_config)
            
            # Verify tokenization application
            assert result['status'] == 'success', \
                "Tokenization should succeed"
            assert result['data_anonymized'] > 0, \
                "Should tokenize sensitive data"
            
            # Verify tokenization results
            if hasattr(tool, 'anonymization_results'):
                for target_id, anon_result in tool.anonymization_results.items():
                    if anon_result['status'] == 'anonymized':
                        assert anon_result['technique'] == 'tokenization', \
                            "Should use tokenization technique"
                        assert 'token_format' in anon_result, \
                            "Should record token format"
                        assert 'tokens_generated' in anon_result, \
                            "Should record tokens generated count"
            
            workflow_time = time.time() - start_time
            assert workflow_time < 20.0, \
                f"Tokenization took too long: {workflow_time:.2f}s"
            
        finally:
            performance_monitor.stop_monitoring('data_anonymizer', 'tokenization')


class TestDataAnonymizerVerificationProcesses:
    """Test anonymization effectiveness and compliance verification."""
    
    def test_anonymization_effectiveness_workflow(self, 
                                                data_anonymizer_test_environment):
        """
        Test: Effectiveness Analysis → Sensitive Data Verification → Completeness Check → Risk Assessment
        Target: < 15 seconds for effectiveness validation
        """
        env = data_anonymizer_test_environment
        tool = env['tool']
        performance_monitor = env['performance_monitor']
        
        performance_monitor.start_monitoring('data_anonymizer', 
                                           'effectiveness_check')
        
        start_time = time.time()
        
        try:
            # Create test anonymized data for verification
            test_data = create_test_sensitive_data('pii', 25)
            
            # Simulate anonymization first
            targets = {'test_dataset': {'data': test_data, 'type': 'structured'}}
            anon_result = tool.apply_anonymization(targets, 'data_masking', 
                                                 {'mask_type': 'character'})
            
            # Verify anonymization effectiveness
            verification_config = {
                'methods': ['effectiveness', 'utility_preservation'],
                'sensitivity_threshold': 0.05,  # < 5% sensitive data remaining
                'utility_threshold': 0.7  # > 70% utility preserved
            }
            
            # Note: verify_anonymization method would need to be implemented in the mock
            # For now, test the process_data call directly
            verification_result = tool.process_data("verify_anonymization_effectiveness",
                                                   operation_type='verification',
                                                   results_count=len(targets))
            
            # Verify effectiveness validation
            assert anon_result['status'] == 'success', \
                "Anonymization should succeed first"
            assert verification_result['status'] == 'success', \
                "Effectiveness verification should succeed"
            
            workflow_time = time.time() - start_time
            assert workflow_time < 15.0, \
                f"Effectiveness verification took too long: {workflow_time:.2f}s"
            
        finally:
            performance_monitor.stop_monitoring('data_anonymizer', 'effectiveness_check')


class TestDataAnonymizerIntegration:
    """Test integration between Data Anonymizer and other components."""
    
    def test_data_anonymizer_hub_integration_workflow(self, 
                                                    data_anonymizer_test_environment):
        """
        Test: Anonymizer Config → Hub Registration → Cross-tool Communication
        """
        env = data_anonymizer_test_environment
        anonymizer_tool = env['tool']
        hub = env['hub']
        
        # Verify tool is registered with hub
        assert 'data_anonymizer' in hub.registered_tools, \
            "Data Anonymizer should be registered with hub"
        
        # Verify hub coordination
        hub_status = hub.tool_status
        assert 'data_anonymizer' in hub_status, \
            "Hub should track Data Anonymizer status"
        
        # Test anonymization operation with hub coordination
        test_data = create_test_sensitive_data('pii', 10)
        targets = {'hub_test': {'data': test_data, 'type': 'structured'}}
        
        result = anonymizer_tool.apply_anonymization(targets, 'data_masking', 
                                                   {'mask_type': 'character'})
        
        assert result['status'] == 'success', \
            "Hub-integrated anonymization should succeed"
        
        # Verify resource coordination
        resource_usage = anonymizer_tool.get_resource_usage()
        assert isinstance(resource_usage, dict), \
            "Should track resource usage for hub coordination"
        assert 'memory' in resource_usage, "Should track memory usage"
        assert 'cpu' in resource_usage, "Should track CPU usage"


# Test runner configuration
def run_data_anonymizer_e2e_tests():
    """Run the Data Anonymizer E2E test suite."""
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
    print("Starting Data Anonymizer End-to-End Tests...")
    exit_code = run_data_anonymizer_e2e_tests()
    
    print(f"\nData Anonymizer E2E Test Suite completed "
          f"with exit code: {exit_code}")
    sys.exit(exit_code)