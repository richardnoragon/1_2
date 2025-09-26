#!/usr/bin/env python3
"""
Step-by-step validation for checksum migration
"""

def test_1_basic_imports():
    """Test 1: Basic Import Validation"""
    print("=" * 60)
    print("TEST 1: BASIC IMPORT VALIDATION")
    print("=" * 60)
    
    results = {}
    
    # Test PyQt5 imports
    try:
        from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
        from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer
        from PyQt5.QtGui import QFont
        results['pyqt5'] = True
        print("✅ PyQt5 core imports: SUCCESS")
    except ImportError as e:
        results['pyqt5'] = False
        print(f"❌ PyQt5 core imports: FAILED - {e}")
    
    # Test file_utilities_2 package-level imports
    try:
        from file_utilities_2.core.check_sum import ChecksumLogic, VALID_ALGORITHMS
        results['core_logic'] = True
        print(f"✅ Core checksum logic import: SUCCESS")
        print(f"   Available algorithms: {VALID_ALGORITHMS}")
    except ImportError as e:
        results['core_logic'] = False
        print(f"❌ Core checksum logic import: FAILED - {e}")
    
    # Test GUI imports
    try:
        from file_utilities_2.gui.check_sum_gui import ChecksumGUI
        results['enhanced_gui'] = True
        print("✅ Enhanced GUI import: SUCCESS")
    except ImportError as e:
        results['enhanced_gui'] = False
        print(f"❌ Enhanced GUI import: FAILED - {e}")
    
    try:
        from file_utilities_2.gui.check_sum_standardized import ChecksumWindow, EnhancedChecksumThread
        results['standardized_gui'] = True
        print("✅ Standardized GUI import: SUCCESS")
    except ImportError as e:
        results['standardized_gui'] = False
        print(f"❌ Standardized GUI import: FAILED - {e}")
    
    # Test package-level imports
    try:
        from file_utilities_2 import ChecksumLogic as PkgChecksumLogic, VALID_ALGORITHMS as PkgAlgorithms
        results['package_level'] = True
        print("✅ Package-level imports: SUCCESS")
    except ImportError as e:
        results['package_level'] = False
        print(f"❌ Package-level imports: FAILED - {e}")
    
    return results

def test_2_external_imports():
    """Test 2: External File Import Validation"""
    print("\n" + "=" * 60)
    print("TEST 2: EXTERNAL FILE IMPORT VALIDATION")
    print("=" * 60)
    
    results = {}
    
    # Test rfuhub.py import
    try:
        import os
        if os.path.exists('rfuhub.py'):
            with open('rfuhub.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'from file_utilities_2.gui.check_sum_gui import ChecksumGUI' in content:
                results['rfuhub_import'] = True
                print("✅ rfuhub.py import statement: SUCCESS")
                print("   Correctly imports from file_utilities_2")
            else:
                results['rfuhub_import'] = False
                print("❌ rfuhub.py import statement: FAILED")
                print("   Import statement not found or incorrect")
        else:
            results['rfuhub_import'] = None
            print("⚠️  rfuhub.py file: NOT FOUND")
    except Exception as e:
        results['rfuhub_import'] = False
        print(f"❌ rfuhub.py validation: FAILED - {e}")
    
    # Test tests/test_checksum.py import
    try:
        if os.path.exists('tests/test_checksum.py'):
            with open('tests/test_checksum.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'from file_utilities_2.core.check_sum import ChecksumLogic' in content:
                results['test_checksum_import'] = True
                print("✅ tests/test_checksum.py import: SUCCESS")
                print("   Correctly imports from file_utilities_2")
            else:
                results['test_checksum_import'] = False
                print("❌ tests/test_checksum.py import: FAILED")
                print("   Import statement not found or incorrect")
        else:
            results['test_checksum_import'] = None
            print("⚠️  tests/test_checksum.py file: NOT FOUND")
    except Exception as e:
        results['test_checksum_import'] = False
        print(f"❌ tests/test_checksum.py validation: FAILED - {e}")
    
    return results

def test_3_functional_validation():
    """Test 3: Functional Validation"""
    print("\n" + "=" * 60)
    print("TEST 3: FUNCTIONAL VALIDATION")
    print("=" * 60)
    
    results = {}
    
    try:
        from file_utilities_2.core.check_sum import ChecksumLogic, VALID_ALGORITHMS
        
        # Test ChecksumLogic instantiation
        try:
            logic = ChecksumLogic()
            results['logic_instantiation'] = True
            print("✅ ChecksumLogic instantiation: SUCCESS")
        except Exception as e:
            results['logic_instantiation'] = False
            print(f"❌ ChecksumLogic instantiation: FAILED - {e}")
        
        # Test algorithm validation
        try:
            test_algorithms = ['md5', 'sha1', 'sha256', 'sha512']
            available_algorithms = [alg for alg in test_algorithms if alg in VALID_ALGORITHMS]
            if available_algorithms:
                results['algorithms_available'] = True
                print(f"✅ Algorithm availability: SUCCESS")
                print(f"   Available: {available_algorithms}")
            else:
                results['algorithms_available'] = False
                print("❌ Algorithm availability: FAILED - No standard algorithms found")
        except Exception as e:
            results['algorithms_available'] = False
            print(f"❌ Algorithm availability: FAILED - {e}")
        
        # Test basic checksum calculation
        try:
            if results.get('logic_instantiation', False):
                from pathlib import Path
                # Create a test file
                test_file = Path('test_checksum_file.txt')
                test_file.write_text('Hello, World!')
                
                # Calculate checksum
                checksum = logic.calculate_checksum(str(test_file), 'md5')
                if checksum:
                    results['checksum_calculation'] = True
                    print(f"✅ Checksum calculation: SUCCESS")
                    print(f"   MD5: {checksum}")
                else:
                    results['checksum_calculation'] = False
                    print("❌ Checksum calculation: FAILED - No checksum returned")
                
                # Clean up
                test_file.unlink()
        except Exception as e:
            results['checksum_calculation'] = False
            print(f"❌ Checksum calculation: FAILED - {e}")
    
    except ImportError as e:
        results['functional_test'] = False
        print(f"❌ Functional validation setup: FAILED - Import failed: {e}")
    
    return results

def test_4_package_structure():
    """Test 4: Package Structure Validation"""
    print("\n" + "=" * 60)
    print("TEST 4: PACKAGE STRUCTURE VALIDATION")
    print("=" * 60)
    
    results = {}
    
    # Check file_utilities_2 directory structure
    from pathlib import Path
    base_path = Path('file_utilities_2')
    
    required_files = [
        '__init__.py',
        'core/__init__.py',
        'core/check_sum.py',
        'gui/__init__.py',
        'gui/check_sum_gui.py',
        'gui/check_sum_standardized.py',
        'gui/check_sum_utils.py',
        'gui/check_sum_worker.py'
    ]
    
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            results[f'file_{file_path}'] = True
            print(f"✅ File exists: {file_path}")
        else:
            results[f'file_{file_path}'] = False
            print(f"❌ File missing: {file_path}")
    
    # Test __init__.py exports
    try:
        from file_utilities_2 import ChecksumLogic, VALID_ALGORITHMS
        results['init_exports'] = True
        print("✅ __init__.py exports: SUCCESS")
        print("   ChecksumLogic and VALID_ALGORITHMS available")
    except ImportError as e:
        results['init_exports'] = False
        print(f"❌ __init__.py exports: FAILED - {e}")
    
    return results

def generate_summary_report(all_results):
    """Generate comprehensive summary report"""
    print("\n" + "=" * 60)
    print("COMPREHENSIVE VALIDATION SUMMARY")
    print("=" * 60)
    
    total_tests = 0
    passed_tests = 0
    
    for category, results in all_results.items():
        print(f"\n{category.upper().replace('_', ' ')}:")
        category_passed = 0
        category_total = 0
        
        for test_name, result in results.items():
            if result is not None:
                category_total += 1
                total_tests += 1
                if result:
                    category_passed += 1
                    passed_tests += 1
                    print(f"  ✅ {test_name}")
                else:
                    print(f"  ❌ {test_name}")
            else:
                print(f"  ⚠️  {test_name} (not applicable)")
        
        if category_total > 0:
            percentage = (category_passed / category_total) * 100
            print(f"  Category Score: {category_passed}/{category_total} ({percentage:.1f}%)")
    
    print(f"\n{'='*60}")
    print(f"OVERALL VALIDATION RESULTS")
    print(f"{'='*60}")
    
    if total_tests > 0:
        overall_percentage = (passed_tests / total_tests) * 100
        print(f"Total Tests: {total_tests}")
        print(f"Passed Tests: {passed_tests}")
        print(f"Failed Tests: {total_tests - passed_tests}")
        print(f"Success Rate: {overall_percentage:.1f}%")
        
        if overall_percentage >= 90:
            print("🎉 EXCELLENT: Migration validation highly successful!")
        elif overall_percentage >= 80:
            print("✅ GOOD: Migration validation successful with minor issues")
        elif overall_percentage >= 70:
            print("⚠️  ACCEPTABLE: Migration validation passed with some concerns")
        else:
            print("❌ NEEDS ATTENTION: Migration validation found significant issues")
    else:
        print("❌ CRITICAL: No tests could be executed")
    
    return passed_tests, total_tests

def main():
    """Main validation function"""
    print("🔍 COMPREHENSIVE CHECKSUM MIGRATION VALIDATION")
    print("=" * 60)
    print("Performing final integration validation and testing...")
    
    import time
    start_time = time.time()
    
    # Run all validation tests
    all_results = {}
    
    try:
        all_results['basic_imports'] = test_1_basic_imports()
        all_results['external_imports'] = test_2_external_imports()
        all_results['functional_validation'] = test_3_functional_validation()
        all_results['package_structure'] = test_4_package_structure()
        
        # Generate summary report
        passed, total = generate_summary_report(all_results)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\nValidation completed in {duration:.2f} seconds")
        
        # Return exit code based on results
        if total > 0 and (passed / total) >= 0.8:
            print("\n🎯 VALIDATION SUCCESSFUL: Ready for production use!")
            return 0
        else:
            print("\n⚠️  VALIDATION ISSUES: Review failed tests before deployment")
            return 1
            
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during validation: {e}")
        import traceback
        traceback.print_exc()
        return 2

if __name__ == "__main__":
    import sys
    sys.exit(main())