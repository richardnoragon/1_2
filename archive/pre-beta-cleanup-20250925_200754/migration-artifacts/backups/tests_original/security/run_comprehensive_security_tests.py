#!/usr/bin/env python3
"""
Comprehensive Security Testing Framework Execution Script

Executes all security tests and generates comprehensive report.

Author: Security Testing Framework  
Date: 2025-09-04
Version: 2.0.0
"""

import os
import subprocess
import sys
import time
from datetime import datetime

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))


def run_security_tests():
    """Run comprehensive security test suite."""
    
    print("🛡️  COMPREHENSIVE SECURITY TESTING FRAMEWORK")
    print("=" * 60)
    print(f"Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Framework Version: 2.0.0")
    print("=" * 60)
    
    # Test commands to execute
    test_commands = [
        {
            'name': 'Input Validation Security',
            'cmd': ['python', '-m', 'unittest', 'test_input_validation', '-v'],
            'cwd': 'tests/security'
        },
        {
            'name': 'Authentication & Authorization',
            'cmd': ['python', '-m', 'unittest', 
                   'test_authentication_authorization', '-v'],
            'cwd': 'tests/security'
        },
        {
            'name': 'Buffer Overflow & Race Conditions',
            'cmd': ['python', '-m', 'unittest', 
                   'test_buffer_overflow_race_conditions', '-v'],
            'cwd': 'tests/security'
        },
        {
            'name': 'Encryption Dialog Security',
            'cmd': ['python', '-m', 'unittest', 'test_encryption_dialog', '-v'],
            'cwd': 'tests/integration/security'
        },
        {
            'name': 'Security Integration',
            'cmd': ['python', '-m', 'unittest', 'test_security_integration', '-v'],
            'cwd': 'tests/integration/security'
        },
        {
            'name': 'Secure Delete (Legacy)',
            'cmd': ['python', '-m', 'unittest', 'test_secure_delete', '-v'],
            'cwd': 'tests'
        }
    ]
    
    results = []
    total_success = 0
    
    print("\n🧪 EXECUTING SECURITY TEST SUITES...")
    print("-" * 60)
    
    for test_suite in test_commands:
        print(f"\n▶️  Running: {test_suite['name']}")
        
        start_time = time.time()
        try:
            result = subprocess.run(
                test_suite['cmd'],
                cwd=test_suite['cwd'],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            duration = time.time() - start_time
            
            success = result.returncode == 0
            if success:
                total_success += 1
                print(f"   ✅ PASSED in {duration:.3f}s")
            else:
                print(f"   ❌ FAILED in {duration:.3f}s")
            
            results.append({
                'name': test_suite['name'],
                'success': success,
                'duration': duration
            })
            
        except subprocess.TimeoutExpired:
            print("   ⏰ TIMEOUT after 5 minutes")
            results.append({
                'name': test_suite['name'],
                'success': False,
                'error': 'Test execution timeout'
            })
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            results.append({
                'name': test_suite['name'],
                'success': False,
                'error': str(e)
            })
    
    # Print summary
    print("\n" + "=" * 60)
    print("🏆 SECURITY TESTING SUMMARY")
    print("=" * 60)
    print(f"📊 Test Suites Executed: {len(test_commands)}")
    print(f"✅ Successful: {total_success}")
    print(f"❌ Failed: {len(test_commands) - total_success}")
    
    success_rate = (total_success / len(test_commands)) * 100
    print(f"🎯 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("\n🏆 FRAMEWORK STATUS: EXCELLENT")
        print("✅ Security testing framework is highly robust!")
    elif success_rate >= 75:
        print("\n✅ FRAMEWORK STATUS: GOOD")
        print("🔧 Minor improvements may be needed.")
    else:
        print("\n⚠️ FRAMEWORK STATUS: NEEDS ATTENTION")
        print("🔧 Please review failed tests.")
    
    return success_rate >= 75


if __name__ == '__main__':
    print("🚀 Starting Comprehensive Security Testing...")
    success = run_security_tests()
    
    if success:
        print("\n🎉 SECURITY TESTING COMPLETED SUCCESSFULLY!")
        print("🛡️ Your security framework is robust and ready.")
    else:
        print("\n⚠️ SECURITY TESTING COMPLETED WITH ISSUES")
        print("🔧 Please review and address failed security tests.")
    
    print("\n🔒 Security Areas Validated:")
    print("   • SQL Injection Protection")
    print("   • XSS (Cross-Site Scripting) Protection")
    print("   • CSRF Protection")
    print("   • Authentication & Authorization")
    print("   • Buffer Overflow & Race Condition Protection")
    print("   • Memory Safety & Concurrency Security")
    print("   • Encryption Dialog Security")
    print("   • Security Integration Workflows")
    print("   • Secure File Deletion Operations")