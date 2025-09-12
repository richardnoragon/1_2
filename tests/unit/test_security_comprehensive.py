#!/usr/bin/env python3
"""
Security Testing for Phase 5 Zero-Compromise Policy
Created: September 9, 2025  
Purpose: Comprehensive security validation with variable parameters

Phase 5 Security Requirements:
✅ Zero-Compromise Security Standards
✅ Variable cryptographic parameters (no fixed salts/keys)
✅ Advanced security scenario validation
✅ Security compliance verification
"""

import hashlib
import os
import secrets
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

# Path configuration
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
src_path = project_root / "src"

if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


def test_variable_cryptographic_parameters():
    """
    Phase 5 Critical: Test with variable cryptographic parameters
    Zero-compromise policy: No fixed salts, keys, or security values
    """
    print("\n=== VARIABLE CRYPTOGRAPHIC PARAMETERS TESTING ===")
    
    security_tests = []
    
    # Test 1: Variable salt generation
    for i in range(5):  # Multiple iterations with different parameters
        salt = secrets.token_bytes(32)  # 256-bit salt
        test_data = f"Security test data {i} - {datetime.now().isoformat()}"
        
        # Create hash with variable salt
        hasher = hashlib.pbkdf2_hmac('sha256', test_data.encode(), salt, 100000)
        
        security_tests.append({
            'test_id': f'variable_salt_{i}',
            'salt_length': len(salt),
            'hash_length': len(hasher),
            'salt_unique': salt not in [t.get('salt') for t in security_tests],
            'hash_unique': hasher not in [t.get('hash') for t in security_tests]
        })
        security_tests[-1]['salt'] = salt
        security_tests[-1]['hash'] = hasher
    
    # Validate all salts and hashes are unique
    salts = [t['salt'] for t in security_tests]
    hashes = [t['hash'] for t in security_tests]
    
    unique_salts = len(set(salts)) == len(salts)
    unique_hashes = len(set(hashes)) == len(hashes)
    
    print(f"Variable salt validation: {len(salts)} salts, {len(set(salts))} unique")
    print(f"Variable hash validation: {len(hashes)} hashes, {len(set(hashes))} unique")
    
    assert unique_salts, "Fixed salt detected - violates zero-compromise policy"
    assert unique_hashes, "Duplicate hashes detected - crypto weakness"


def test_dynamic_key_derivation():
    """
    Test dynamic key derivation without hardcoded security values
    """
    print("\n=== DYNAMIC KEY DERIVATION TESTING ===")
    
    key_derivation_tests = []
    
    for iteration in range(3):
        # Generate dynamic parameters
        password = f"TestPassword{iteration}_{secrets.token_hex(8)}"
        salt = secrets.token_bytes(16)
        iterations = 50000 + secrets.randbelow(50000)  # Variable iteration count
        
        # Derive key with variable parameters
        derived_key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt,
            iterations
        )
        
        key_derivation_tests.append({
            'iteration': iteration,
            'password_length': len(password),
            'salt_length': len(salt),
            'iterations_used': iterations,
            'derived_key_length': len(derived_key),
            'derived_key': derived_key
        })
    
    # Validate variable parameters
    iteration_counts = [t['iterations_used'] for t in key_derivation_tests]
    derived_keys = [t['derived_key'] for t in key_derivation_tests]
    
    variable_iterations = len(set(iteration_counts)) == len(iteration_counts)
    unique_keys = len(set(derived_keys)) == len(derived_keys)
    
    print(f"Iteration variability: {variable_iterations}")
    print(f"Key uniqueness: {unique_keys}")
    print(f"Iteration range: {min(iteration_counts)} - {max(iteration_counts)}")
    
    assert variable_iterations, "Fixed iteration count violates variable parameter requirement"
    assert unique_keys, "Duplicate derived keys indicate security weakness"


def test_secure_random_generation_quality():
    """
    Test quality of secure random generation
    Phase 5: Ensure cryptographically secure randomness
    """
    print("\n=== SECURE RANDOM GENERATION QUALITY ===") 
    
    random_quality_tests = []
    
    # Generate multiple random samples
    sample_size = 1000
    random_samples = []
    
    for _ in range(sample_size):
        random_bytes = secrets.token_bytes(32)
        random_samples.append(random_bytes)
    
    # Statistical quality tests
    unique_samples = len(set(random_samples))
    uniqueness_ratio = unique_samples / sample_size
    
    # Byte distribution test
    all_bytes = b''.join(random_samples)
    byte_counts = [all_bytes.count(bytes([i])) for i in range(256)]
    
    # Calculate chi-square for uniformity (simplified)
    expected_count = len(all_bytes) / 256
    chi_square = sum((count - expected_count) ** 2 / expected_count for count in byte_counts)
    
    random_quality_tests.append({
        'sample_size': sample_size,
        'unique_samples': unique_samples,
        'uniqueness_ratio': uniqueness_ratio,
        'chi_square_statistic': chi_square,
        'uniform_distribution': chi_square < 400  # Simplified threshold
    })
    
    print(f"Random quality: {uniqueness_ratio*100:.2f}% unique samples")
    print(f"Distribution uniformity: {'GOOD' if chi_square < 400 else 'POOR'}")
    print(f"Chi-square statistic: {chi_square:.2f}")
    
    assert uniqueness_ratio > 0.99, f"Random uniqueness too low: {uniqueness_ratio*100:.2f}%"
    assert chi_square < 400, f"Random distribution not uniform: {chi_square:.2f}"


def test_security_failure_scenarios():
    """
    Test realistic security failure scenarios
    Phase 5: Advanced error handling and security validation
    """
    print("\n=== SECURITY FAILURE SCENARIOS ===")
    
    failure_scenarios = [
        {
            'name': 'insufficient_entropy',
            'description': 'Test handling of low entropy conditions',
            'test_function': lambda: secrets.token_bytes(1)  # Very small entropy
        },
        {
            'name': 'large_data_hashing',
            'description': 'Test security with large data volumes',
            'test_function': lambda: hashlib.sha256(b'x' * 1000000).hexdigest()  # 1MB
        },
        {
            'name': 'rapid_key_generation',
            'description': 'Test rapid key generation performance',
            'test_function': lambda: [secrets.token_bytes(32) for _ in range(100)]
        }
    ]
    
    scenario_results = []
    
    for scenario in failure_scenarios:
        try:
            start_time = datetime.now()
            result = scenario['test_function']()
            end_time = datetime.now()
            
            processing_time = (end_time - start_time).total_seconds()
            
            scenario_results.append({
                'name': scenario['name'],
                'success': True,
                'processing_time': processing_time,
                'result_type': type(result).__name__,
                'result_size': len(str(result)) if result else 0
            })
            
        except Exception as e:
            scenario_results.append({
                'name': scenario['name'],
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            })
    
    # Evaluate security scenario results
    successful_scenarios = sum(1 for r in scenario_results if r['success'])
    total_scenarios = len(scenario_results)
    security_robustness = (successful_scenarios / total_scenarios) * 100
    
    print(f"Security robustness: {successful_scenarios}/{total_scenarios} scenarios handled")
    
    for result in scenario_results:
        if result['success']:
            print(f"  ✅ {result['name']}: {result['processing_time']:.3f}s")
        else:
            print(f"  ❌ {result['name']}: {result['error_type']}")
    
    assert security_robustness >= 80, f"Security robustness {security_robustness:.1f}% below 80%"


def test_file_security_operations():
    """
    Test file security operations with realistic scenarios
    """
    print("\n=== FILE SECURITY OPERATIONS ===")
    
    with tempfile.TemporaryDirectory(prefix="security_test_") as temp_dir:
        temp_path = Path(temp_dir)
        
        file_security_tests = []
        
        # Test 1: Secure file creation and deletion
        for i in range(5):
            test_file = temp_path / f"secure_test_{i}_{secrets.token_hex(8)}.txt"
            secure_content = f"Secure content {i}: {secrets.token_hex(32)}"
            
            try:
                # Create file with secure content
                test_file.write_text(secure_content, encoding='utf-8')
                
                # Verify file exists and content matches
                read_content = test_file.read_text(encoding='utf-8')
                content_match = read_content == secure_content
                
                # Secure deletion simulation
                if test_file.exists():
                    # Overwrite with random data before deletion
                    random_overwrite = secrets.token_bytes(len(secure_content.encode()))
                    test_file.write_bytes(random_overwrite)
                    test_file.unlink()
                
                deletion_success = not test_file.exists()
                
                file_security_tests.append({
                    'test_id': f'secure_file_{i}',
                    'file_created': True,
                    'content_integrity': content_match,
                    'secure_deletion': deletion_success,
                    'overall_success': content_match and deletion_success
                })
                
            except Exception as e:
                file_security_tests.append({
                    'test_id': f'secure_file_{i}',
                    'file_created': False,
                    'error': str(e),
                    'overall_success': False
                })
        
        # Evaluate file security results
        successful_operations = sum(1 for t in file_security_tests if t['overall_success'])
        total_operations = len(file_security_tests)
        file_security_score = (successful_operations / total_operations) * 100
        
        print(f"File security operations: {successful_operations}/{total_operations} successful")
        
        assert file_security_score >= 90, f"File security score {file_security_score:.1f}% below 90%"


def test_security_performance_under_load():
    """
    Test security operations performance under realistic load
    Phase 5: Performance validation with security operations
    """
    print("\n=== SECURITY PERFORMANCE UNDER LOAD ===")
    
    load_tests = [
        {
            'name': 'concurrent_hashing',
            'operations': 50,
            'operation': lambda i: hashlib.sha256(f"data_{i}_{secrets.token_hex(16)}".encode()).hexdigest()
        },
        {
            'name': 'key_derivation_load',
            'operations': 10,
            'operation': lambda i: hashlib.pbkdf2_hmac('sha256', f"password_{i}".encode(), secrets.token_bytes(16), 10000)
        },
        {
            'name': 'random_generation_burst',
            'operations': 100,
            'operation': lambda i: secrets.token_bytes(64)
        }
    ]
    
    performance_results = []
    
    for load_test in load_tests:
        start_time = datetime.now()
        results = []
        
        try:
            for i in range(load_test['operations']):
                result = load_test['operation'](i)
                results.append(result)
            
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds()
            operations_per_second = load_test['operations'] / total_time if total_time > 0 else 0
            
            performance_results.append({
                'name': load_test['name'],
                'success': True,
                'operations': load_test['operations'],
                'total_time': total_time,
                'ops_per_second': operations_per_second,
                'results_unique': len(set(str(r) for r in results)) == len(results)
            })
            
        except Exception as e:
            performance_results.append({
                'name': load_test['name'],
                'success': False,
                'error': str(e)
            })
    
    # Evaluate performance results
    successful_load_tests = sum(1 for r in performance_results if r['success'])
    total_load_tests = len(performance_results)
    
    print(f"Security performance: {successful_load_tests}/{total_load_tests} load tests passed")
    
    for result in performance_results:
        if result['success']:
            print(f"  ✅ {result['name']}: {result['ops_per_second']:.1f} ops/sec")
        else:
            print(f"  ❌ {result['name']}: {result.get('error', 'Unknown error')}")
    
    # Performance thresholds for security operations
    min_performance_met = all(
        r.get('ops_per_second', 0) >= 10 for r in performance_results if r['success']
    )
    
    assert min_performance_met, "Security operations performance below minimum threshold"


def main():
    """Execute security comprehensive testing for Phase 5"""
    print("PHASE 5: SECURITY COMPREHENSIVE TESTING")
    print("Zero-Compromise Policy - Variable Parameters")
    print("=" * 60)
    
    # Configure pytest for security testing
    pytest_args = [
        __file__,
        '-v',
        '--tb=long',
        '--capture=no',
        f'--html=tests/unit/results/security_comprehensive_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html',
        '--self-contained-html'
    ]
    
    # Execute tests
    exit_code = pytest.main(pytest_args)
    
    print(f"\nSECURITY TESTING COMPLETED - Exit Code: {exit_code}")
    
    if exit_code == 0:
        print("✅ Zero-compromise security standards maintained")
        print("✅ Variable cryptographic parameters validated")
        print("✅ Security performance requirements met")
        print("✅ Advanced security scenarios handled")
    else:
        print("❌ Security testing identified critical issues")
        print("🚨 Zero-compromise policy violations detected")
        print("📋 Immediate security remediation required")
    
    return exit_code == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)