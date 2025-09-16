#!/usr/bin/env python3
"""
Validation Script for Enhanced Security Validator Test Setup
===========================================================

Script: validate_enhanced_test_setup_2025-08-30.py
Purpose: Verify all enhanced test infrastructure components are working correctly
Generated: 2025-08-30T10:12:00Z

This script validates:
- All required files exist and are properly configured
- Dependencies are correctly installed
- Test infrastructure functions as expected
- Enhanced features are operational
"""

import importlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple


class EnhancedTestSetupValidator:
    """Validator for enhanced test setup."""
    
    def __init__(self):
        """Initialize the validator."""
        self.test_dir = Path(__file__).parent
        self.validation_results = []
        self.errors = []
        self.warnings = []
        
    def log_result(self, check_name: str, passed: bool, message: str, details: str = ""):
        """Log a validation result."""
        self.validation_results.append({
            'check': check_name,
            'passed': passed,
            'message': message,
            'details': details,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {check_name} - {message}")
        
        if details:
            print(f"   Details: {details}")
        
        if not passed:
            self.errors.append(f"{check_name}: {message}")
    
    def log_warning(self, check_name: str, message: str):
        """Log a warning."""
        self.warnings.append(f"{check_name}: {message}")
        print(f"⚠️  WARN: {check_name} - {message}")
    
    def check_required_files(self) -> bool:
        """Check that all required files exist."""
        required_files = [
            'test_security_validator_2025-08-30.py',
            'conftest_security_validator_2025-08-30.py',
            'pytest_security_validator_2025-08-30.ini',
            'requirements_test_security_validator_2025-08-30.txt',
            # Enhanced files
            'pytest_security_validator_enhanced_2025-08-30.ini',
            'conftest_security_validator_enhanced_2025-08-30.py',
            'requirements_test_security_validator_enhanced_2025-08-30.txt',
            'execute_security_validator_tests_enhanced_2025-08-30.py',
            'ENHANCED_TESTING_DOCUMENTATION_security_validator_2025-08-30.md'
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.test_dir / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            self.log_result(
                "Required Files Check",
                False,
                f"Missing {len(missing_files)} required files",
                f"Missing: {', '.join(missing_files)}"
            )
            return False
        else:
            self.log_result(
                "Required Files Check",
                True,
                f"All {len(required_files)} required files found"
            )
            return True
    
    def check_python_dependencies(self) -> bool:
        """Check that required Python packages are available."""
        required_packages = [
            ('pytest', 'pytest'),
            ('coverage', 'coverage'),
            ('pytest_html', 'pytest-html'),
            ('pytest_json_report', 'pytest-json-report'),
            ('pytest_cov', 'pytest-cov'),
            ('pytest_mock', 'pytest-mock')
        ]
        
        optional_packages = [
            ('psutil', 'psutil'),
            ('memory_profiler', 'memory-profiler'),
            ('pytest_benchmark', 'pytest-benchmark')
        ]
        
        missing_required = []
        missing_optional = []
        
        # Check required packages
        for import_name, package_name in required_packages:
            try:
                importlib.import_module(import_name)
            except ImportError:
                missing_required.append(package_name)
        
        # Check optional packages
        for import_name, package_name in optional_packages:
            try:
                importlib.import_module(import_name)
            except ImportError:
                missing_optional.append(package_name)
        
        if missing_required:
            self.log_result(
                "Required Dependencies Check",
                False,
                f"Missing {len(missing_required)} required packages",
                f"Missing: {', '.join(missing_required)}"
            )
            return False
        else:
            self.log_result(
                "Required Dependencies Check",
                True,
                "All required packages available"
            )
        
        if missing_optional:
            self.log_warning(
                "Optional Dependencies Check",
                f"Missing optional packages: {', '.join(missing_optional)} (some features may be limited)"
            )
        
        return True
    
    def check_target_module_import(self) -> bool:
        """Check that the target SecurityValidator module can be imported."""
        try:
            # Add src directory to path
            src_path = self.test_dir.parent.parent / 'src'
            if str(src_path) not in sys.path:
                sys.path.insert(0, str(src_path))
            
            from tools.network.network_connectivity_complex.core.security_validator import (
                SecurityLevel, SecurityRule, SecurityValidator,
                ValidationResponse, ValidationResult)

            # Try to instantiate the class
            validator = SecurityValidator()
            
            self.log_result(
                "Target Module Import",
                True,
                "SecurityValidator module imported successfully"
            )
            return True
            
        except ImportError as e:
            self.log_result(
                "Target Module Import",
                False,
                "Failed to import SecurityValidator module",
                str(e)
            )
            return False
    
    def check_test_file_syntax(self) -> bool:
        """Check that test files have valid Python syntax."""
        test_files = [
            'test_security_validator_2025-08-30.py',
            'conftest_security_validator_2025-08-30.py',
            'conftest_security_validator_enhanced_2025-08-30.py',
            'execute_security_validator_tests_enhanced_2025-08-30.py'
        ]
        
        syntax_errors = []
        
        for test_file in test_files:
            file_path = self.test_dir / test_file
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    compile(content, str(file_path), 'exec')
                    
                except SyntaxError as e:
                    syntax_errors.append(f"{test_file}: {e}")
                except Exception as e:
                    syntax_errors.append(f"{test_file}: {e}")
        
        if syntax_errors:
            self.log_result(
                "Test File Syntax Check",
                False,
                f"Syntax errors in {len(syntax_errors)} files",
                "; ".join(syntax_errors)
            )
            return False
        else:
            self.log_result(
                "Test File Syntax Check",
                True,
                f"All {len(test_files)} test files have valid syntax"
            )
            return True
    
    def generate_validation_report(self) -> Dict:
        """Generate a comprehensive validation report."""
        passed_checks = sum(1 for result in self.validation_results if result['passed'])
        total_checks = len(self.validation_results)
        
        report = {
            'validation_summary': {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'total_checks': total_checks,
                'passed_checks': passed_checks,
                'failed_checks': total_checks - passed_checks,
                'warnings': len(self.warnings),
                'success_rate': (passed_checks / total_checks * 100) if total_checks > 0 else 0
            },
            'detailed_results': self.validation_results,
            'errors': self.errors,
            'warnings': self.warnings,
            'recommendations': []
        }
        
        # Generate recommendations
        if self.errors:
            report['recommendations'].append("Fix all failed checks before running tests")
        
        if self.warnings:
            report['recommendations'].append("Consider installing optional packages for full functionality")
        
        if passed_checks == total_checks:
            report['recommendations'].append("All checks passed - ready to run enhanced tests")
        
        return report
    
    def run_validation(self) -> bool:
        """Run all validation checks."""
        print("=" * 60)
        print("Enhanced Security Validator Test Setup Validation")
        print("=" * 60)
        print()
        
        # Run all validation checks
        checks = [
            self.check_required_files,
            self.check_python_dependencies,
            self.check_target_module_import,
            self.check_test_file_syntax
        ]
        
        all_passed = True
        for check in checks:
            try:
                result = check()
                if not result:
                    all_passed = False
            except Exception as e:
                self.log_result(
                    check.__name__,
                    False,
                    f"Unexpected error: {e}"
                )
                all_passed = False
            print()
        
        # Generate and save report
        report = self.generate_validation_report()
        
        report_file = self.test_dir / 'result_security_validator_validation_2025-08-30.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Print summary
        print("=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Total Checks: {report['validation_summary']['total_checks']}")
        print(f"Passed: {report['validation_summary']['passed_checks']}")
        print(f"Failed: {report['validation_summary']['failed_checks']}")
        print(f"Warnings: {report['validation_summary']['warnings']}")
        print(f"Success Rate: {report['validation_summary']['success_rate']:.1f}%")
        print()
        
        if self.errors:
            print("❌ ERRORS TO FIX:")
            for error in self.errors:
                print(f"  - {error}")
            print()
        
        if self.warnings:
            print("⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  - {warning}")
            print()
        
        if all_passed:
            print("✅ ALL CHECKS PASSED - Enhanced test setup is ready!")
        else:
            print("❌ SOME CHECKS FAILED - Please fix issues before running tests")
        
        print(f"\nDetailed report saved to: {report_file}")
        
        return all_passed


def main():
    """Main entry point."""
    validator = EnhancedTestSetupValidator()
    success = validator.run_validation()
    
    if success:
        print("\n🚀 Ready to run enhanced tests:")
        print("   python execute_security_validator_tests_enhanced_2025-08-30.py")
        sys.exit(0)
    else:
        print("\n🔧 Please fix the issues above before proceeding")
        sys.exit(1)


if __name__ == "__main__":
    main()