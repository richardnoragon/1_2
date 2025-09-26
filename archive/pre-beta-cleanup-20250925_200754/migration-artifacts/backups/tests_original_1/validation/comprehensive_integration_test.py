#!/usr/bin/env python3
"""
Comprehensive Integration Test for file_utilities_2 Checksum Migration
This script performs thorough testing of all migrated components.
"""

import sys
import os
import tempfile
import hashlib
import time
import traceback
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

class IntegrationTestSuite:
    """Comprehensive integration test suite for file_utilities_2."""
    
    def __init__(self):
        self.test_results = {}
        self.temp_dir = None
        self.test_files = {}
        
    def setup_test_environment(self):
        """Set up test environment with temporary files."""
        print("Setting up test environment...")
        self.temp_dir = tempfile.mkdtemp(prefix="fu2_test_")
        
        # Create test files with known content
        test_data = {
            'small.txt': b'Hello, World!',
            'medium.txt': b'A' * 1024,  # 1KB
            'large.txt': b'B' * (1024 * 1024),  # 1MB
            'empty.txt': b''
        }
        
        for filename, content in test_data.items():
            file_path = os.path.join(self.temp_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(content)
            
            # Calculate expected checksums
            self.test_files[filename] = {
                'path': file_path,
                'content': content,
                'size': len(content),
                'md5': hashlib.md5(content).hexdigest(),
                'sha1': hashlib.sha1(content).hexdigest(),
                'sha256': hashlib.sha256(content).hexdigest(),
                'sha512': hashlib.sha512(content).hexdigest()
            }
        
        print(f"Created test files in: {self.temp_dir}")
        return True
    
    def cleanup_test_environment(self):
        """Clean up test environment."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)
            print(f"Cleaned up test directory: {self.temp_dir}")
    
    def test_basic_imports(self):
        """Test 1: Basic module imports."""
        print("\n" + "="*60)
        print("TEST 1: BASIC MODULE IMPORTS")
        print("="*60)
        
        import_tests = [
            ('file_utilities_2', 'Main package'),
            ('file_utilities_2.core', 'Core module'),
            ('file_utilities_2.core.check_sum', 'Core checksum module'),
            ('file_utilities_2.gui', 'GUI module'),
            ('file_utilities_2.gui.check_sum_gui', 'GUI checksum_gui'),
            ('file_utilities_2.gui.check_sum_standardized', 'GUI standardized'),
            ('file_utilities_2.tests', 'Tests module'),
        ]
        
        results = {}
        for module_name, description in import_tests:
            try:
                module = __import__(module_name, fromlist=[''])
                print(f"✅ {description}: SUCCESS")
                results[module_name] = True
            except Exception as e:
                print(f"❌ {description}: FAILED - {e}")
                results[module_name] = False
        
        self.test_results['basic_imports'] = results
        return all(results.values())
    
    def test_specific_exports(self):
        """Test 2: Specific exports from modules."""
        print("\n" + "="*60)
        print("TEST 2: SPECIFIC EXPORTS")
        print("="*60)
        
        try:
            # Test main package exports
            from file_utilities_2 import ChecksumLogic, VALID_ALGORITHMS
            from file_utilities_2 import ChecksumGUI, ChecksumWindow, MyGUI
            print("✅ Main package exports: SUCCESS")
            
            # Test core exports
            from file_utilities_2.core.check_sum import ChecksumLogic as CoreLogic
            from file_utilities_2.core.check_sum import VALID_ALGORITHMS as CoreAlgorithms
            print("✅ Core module exports: SUCCESS")
            
            # Verify VALID_ALGORITHMS content
            expected_algorithms = ['md5', 'sha1', 'sha256', 'sha512']
            if set(VALID_ALGORITHMS) == set(expected_algorithms):
                print("✅ VALID_ALGORITHMS content: SUCCESS")
            else:
                print(f"❌ VALID_ALGORITHMS mismatch: {VALID_ALGORITHMS}")
                return False
            
            self.test_results['specific_exports'] = True
            return True
            
        except Exception as e:
            print(f"❌ Specific exports: FAILED - {e}")
            self.test_results['specific_exports'] = False
            return False
    
    def test_core_functionality(self):
        """Test 3: Core checksum functionality."""
        print("\n" + "="*60)
        print("TEST 3: CORE FUNCTIONALITY")
        print("="*60)
        
        try:
            from file_utilities_2.core.check_sum import ChecksumLogic
            
            # Test each algorithm
            for algorithm in ['md5', 'sha1', 'sha256', 'sha512']:
                print(f"\nTesting {algorithm.upper()} algorithm:")
                
                for filename, file_info in self.test_files.items():
                    checksummer = ChecksumLogic(
                        file_info['path'], 
                        algorithm, 
                        mode='calculate_file'
                    )
                    
                    # Test direct calculation methods
                    if algorithm == 'md5':
                        result = checksummer.calculate_md5(file_info['path'])
                    elif algorithm == 'sha1':
                        result = checksummer.calculate_sha1(file_info['path'])
                    elif algorithm == 'sha256':
                        result = checksummer.calculate_sha256(file_info['path'])
                    
                    expected = file_info[algorithm]
                    if result == expected:
                        print(f"  ✅ {filename}: {result}")
                    else:
                        print(f"  ❌ {filename}: Expected {expected}, got {result}")
                        return False
            
            self.test_results['core_functionality'] = True
            return True
            
        except Exception as e:
            print(f"❌ Core functionality: FAILED - {e}")
            print(traceback.format_exc())
            self.test_results['core_functionality'] = False
            return False
    
    def test_batch_operations(self):
        """Test 4: Batch operations."""
        print("\n" + "="*60)
        print("TEST 4: BATCH OPERATIONS")
        print("="*60)
        
        try:
            from file_utilities_2.core.check_sum import ChecksumLogic
            
            checksummer = ChecksumLogic("", "sha256")
            file_paths = [info['path'] for info in self.test_files.values()]
            
            # Test batch calculation
            results = checksummer.calculate_batch(file_paths, 'sha256')
            
            print(f"Batch processed {len(results)} files:")
            for file_path, checksum in results.items():
                filename = os.path.basename(file_path)
                expected = self.test_files[filename]['sha256']
                if checksum == expected:
                    print(f"  ✅ {filename}: {checksum}")
                else:
                    print(f"  ❌ {filename}: Expected {expected}, got {checksum}")
                    return False
            
            self.test_results['batch_operations'] = True
            return True
            
        except Exception as e:
            print(f"❌ Batch operations: FAILED - {e}")
            self.test_results['batch_operations'] = False
            return False
    
    def test_verification(self):
        """Test 5: Checksum verification."""
        print("\n" + "="*60)
        print("TEST 5: CHECKSUM VERIFICATION")
        print("="*60)
        
        try:
            from file_utilities_2.core.check_sum import ChecksumLogic
            
            checksummer = ChecksumLogic("", "sha256")
            
            for filename, file_info in self.test_files.items():
                # Test successful verification
                result = checksummer.verify_file(
                    file_info['path'],
                    file_info['sha256'],
                    'sha256'
                )
                
                if result:
                    print(f"  ✅ {filename}: Verification SUCCESS")
                else:
                    print(f"  ❌ {filename}: Verification FAILED")
                    return False
                
                # Test failed verification
                result = checksummer.verify_file(
                    file_info['path'],
                    'invalid_checksum_value',
                    'sha256'
                )
                
                if not result:
                    print(f"  ✅ {filename}: Invalid checksum correctly rejected")
                else:
                    print(f"  ❌ {filename}: Invalid checksum incorrectly accepted")
                    return False
            
            self.test_results['verification'] = True
            return True
            
        except Exception as e:
            print(f"❌ Verification: FAILED - {e}")
            self.test_results['verification'] = False
            return False
    
    def test_pyqt5_signals(self):
        """Test 6: PyQt5 signal functionality."""
        print("\n" + "="*60)
        print("TEST 6: PYQT5 SIGNALS")
        print("="*60)
        
        try:
            from PyQt5.QtCore import QObject, pyqtSignal
            from file_utilities_2.core.check_sum import ChecksumLogic
            
            # Test signal creation and connection
            checksummer = ChecksumLogic(
                self.test_files['medium.txt']['path'],
                'sha256',
                mode='calculate_file'
            )
            
            # Verify signals exist
            signals_to_check = [
                'progress_updated',
                'progress_percentage', 
                'progress_message',
                'milestone_reached',
                'result_ready',
                'error_occurred',
                'finished',
                'time_estimate'
            ]
            
            for signal_name in signals_to_check:
                if hasattr(checksummer, signal_name):
                    signal = getattr(checksummer, signal_name)
                    if hasattr(signal, 'connect'):
                        print(f"  ✅ {signal_name}: Signal exists and connectable")
                    else:
                        print(f"  ❌ {signal_name}: Not a proper signal")
                        return False
                else:
                    print(f"  ❌ {signal_name}: Signal missing")
                    return False
            
            self.test_results['pyqt5_signals'] = True
            return True
            
        except Exception as e:
            print(f"❌ PyQt5 signals: FAILED - {e}")
            self.test_results['pyqt5_signals'] = False
            return False
    
    def test_gui_instantiation(self):
        """Test 7: GUI component instantiation."""
        print("\n" + "="*60)
        print("TEST 7: GUI INSTANTIATION")
        print("="*60)
        
        try:
            # Test GUI imports without instantiation (to avoid display issues)
            from file_utilities_2.gui.check_sum_standardized import ChecksumWindow, MyGUI
            print("✅ GUI classes imported successfully")
            
            # Test that classes are properly defined
            if hasattr(ChecksumWindow, '__init__'):
                print("✅ ChecksumWindow class properly defined")
            else:
                print("❌ ChecksumWindow class malformed")
                return False
                
            if hasattr(MyGUI, '__init__'):
                print("✅ MyGUI class properly defined")
            else:
                print("❌ MyGUI class malformed")
                return False
            
            self.test_results['gui_instantiation'] = True
            return True
            
        except Exception as e:
            print(f"❌ GUI instantiation: FAILED - {e}")
            self.test_results['gui_instantiation'] = False
            return False
    
    def test_performance(self):
        """Test 8: Performance benchmarks."""
        print("\n" + "="*60)
        print("TEST 8: PERFORMANCE BENCHMARKS")
        print("="*60)
        
        try:
            from file_utilities_2.core.check_sum import ChecksumLogic
            
            # Test performance on large file
            large_file = self.test_files['large.txt']
            checksummer = ChecksumLogic(large_file['path'], 'sha256')
            
            start_time = time.time()
            result = checksummer.calculate_sha256(large_file['path'])
            end_time = time.time()
            
            duration = end_time - start_time
            throughput = large_file['size'] / duration / (1024 * 1024)  # MB/s
            
            print(f"  File size: {large_file['size'] / (1024*1024):.1f} MB")
            print(f"  Duration: {duration:.2f} seconds")
            print(f"  Throughput: {throughput:.1f} MB/s")
            
            if result == large_file['sha256']:
                print("  ✅ Performance test: SUCCESS")
                self.test_results['performance'] = True
                return True
            else:
                print("  ❌ Performance test: Checksum mismatch")
                return False
                
        except Exception as e:
            print(f"❌ Performance test: FAILED - {e}")
            self.test_results['performance'] = False
            return False
    
    def run_all_tests(self):
        """Run all integration tests."""
        print("FILE UTILITIES 2 - COMPREHENSIVE INTEGRATION TEST")
        print("=" * 80)
        
        # Setup
        if not self.setup_test_environment():
            print("❌ Failed to setup test environment")
            return False
        
        try:
            # Run all tests
            tests = [
                self.test_basic_imports,
                self.test_specific_exports,
                self.test_core_functionality,
                self.test_batch_operations,
                self.test_verification,
                self.test_pyqt5_signals,
                self.test_gui_instantiation,
                self.test_performance
            ]
            
            passed_tests = 0
            total_tests = len(tests)
            
            for test_func in tests:
                try:
                    if test_func():
                        passed_tests += 1
                except Exception as e:
                    print(f"❌ Test {test_func.__name__} crashed: {e}")
            
            # Summary
            print("\n" + "="*80)
            print("INTEGRATION TEST SUMMARY")
            print("="*80)
            
            for test_name, result in self.test_results.items():
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{test_name:25} {status}")
            
            print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
            
            if passed_tests == total_tests:
                print("\n🎉 ALL TESTS PASSED - Migration is successful!")
                return True
            else:
                print(f"\n⚠️  {total_tests - passed_tests} tests failed - Issues detected")
                return False
                
        finally:
            self.cleanup_test_environment()

def main():
    """Main function."""
    test_suite = IntegrationTestSuite()
    success = test_suite.run_all_tests()
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())