#!/usr/bin/env python3
"""
Final Test Execution Script for platform_utils.py
Generated on: 2025-08-30

This script provides a simple way to run all tests with full reporting and coverage analysis.
"""

import subprocess
import sys
from pathlib import Path


def run_complete_test_suite():
    """Run the complete test suite with coverage and detailed reporting."""
    
    print("="*80)
    print("Platform Utils Comprehensive Test Execution")
    print("="*80)
    print("Target: platform_utils.py")
    print("Date: 2025-08-30")
    print("Framework: pytest")
    print("="*80)
    
    # Change to the test directory
    test_dir = Path(__file__).parent
    
    # Build the pytest command with all options
    cmd = [
        sys.executable, "-m", "pytest",
        "test_platform_utils_2025-08-30.py",
        "-v",
        "--tb=short",
        "--html=result_platform_utils_2025-08-30.html",
        "--self-contained-html",
        "--json-report",
        "--json-report-file=result_platform_utils_2025-08-30.json",
        "--cov=src.utilities.privacy.privacy_tools.core.platform_utils",
        "--cov-report=html:result_platform_utils_coverage_2025-08-30",
        "--cov-report=term-missing",
        "--cov-report=json:result_platform_utils_coverage_2025-08-30.json",
        "--durations=10"
    ]
    
    try:
        print("Executing test suite...")
        print("Command:", " ".join(cmd))
        print("-" * 80)
        
        # Run the tests
        result = subprocess.run(
            cmd,
            cwd=Path("C:/Users/richardi/1_2"),
            capture_output=False,  # Show output in real-time
            text=True
        )
        
        print("-" * 80)
        print(f"Test execution completed with exit code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ All tests passed successfully!")
        else:
            print("❌ Some tests failed or there were errors.")
        
        # List generated reports
        print("\nGenerated Reports:")
        reports = [
            "result_platform_utils_2025-08-30.html",
            "result_platform_utils_2025-08-30.json",
            "result_platform_utils_coverage_2025-08-30",
            "result_platform_utils_coverage_2025-08-30.json",
            "result_platform_utils_2025-08-30_summary.json"
        ]
        
        for report in reports:
            report_path = test_dir / report
            status = "✓" if report_path.exists() else "✗"
            print(f"  {status} {report}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


if __name__ == "__main__":
    success = run_complete_test_suite()
    sys.exit(0 if success else 1)