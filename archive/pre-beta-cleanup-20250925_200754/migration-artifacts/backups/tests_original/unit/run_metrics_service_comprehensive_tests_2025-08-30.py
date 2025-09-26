#!/usr/bin/env python3
"""
Comprehensive Test Runner for metrics_service.py
Created: 2025-08-30
Purpose: Execute comprehensive unit tests with detailed reporting
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Configuration
TEST_DIR = r"c:\Users\richardi\1_2\tests\unit"
OUTPUT_DIR = TEST_DIR
TEST_FILE = "test_metrics_service_comprehensive_2025-08-30.py"
CONFIG_FILE = "pytest_metrics_service_comprehensive_2025-08-30.ini"
TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def setup_environment():
    """Set up the testing environment."""
    print(f"Setting up test environment at {TIMESTAMP}")
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Change to test directory
    os.chdir(TEST_DIR)
    
    # Set Python path
    sys.path.insert(0, r"c:\Users\richardi\1_2\src\utilities\network\network_connectivity_complex\core")
    
    print(f"Test directory: {TEST_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Test file: {TEST_FILE}")

def run_comprehensive_tests():
    """Run comprehensive tests with multiple report formats."""
    print("\n" + "="*80)
    print("STARTING COMPREHENSIVE METRICS SERVICE TESTS")
    print("="*80)
    
    # Base pytest command
    cmd = [
        sys.executable, "-m", "pytest",
        TEST_FILE,
        "-c", CONFIG_FILE,
        "--verbose",
        "--tb=short",
        f"--cov=metrics_service",
        f"--cov-report=html:coverage_metrics_service_2025-08-30",
        f"--cov-report=json:result_metrics_service_coverage_2025-08-30.json",
        f"--cov-report=term-missing",
        f"--junit-xml=result_metrics_service_2025-08-30.xml",
        f"--html=result_metrics_service_2025-08-30.html",
        "--self-contained-html",
        "--capture=no",
    ]
    
    print(f"Executing command: {' '.join(cmd)}")
    print("\n" + "-"*80)
    
    start_time = time.time()
    
    try:
        # Run tests
        result = subprocess.run(
            cmd,
            cwd=TEST_DIR,
            capture_output=False,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print("\n" + "-"*80)
        print(f"Test execution completed in {execution_time:.2f} seconds")
        print(f"Return code: {result.returncode}")
        
        return result.returncode == 0, execution_time
        
    except subprocess.TimeoutExpired:
        print("\nERROR: Test execution timed out!")
        return False, None
    except Exception as e:
        print(f"\nERROR: Test execution failed: {e}")
        return False, None

def generate_summary_report(success, execution_time):
    """Generate a comprehensive test summary report."""
    print("\n" + "="*80)
    print("GENERATING SUMMARY REPORT")
    print("="*80)
    
    summary = {
        "test_execution": {
            "timestamp": TIMESTAMP,
            "test_file": TEST_FILE,
            "success": success,
            "execution_time_seconds": execution_time,
            "test_directory": TEST_DIR,
            "output_directory": OUTPUT_DIR
        },
        "test_coverage": {
            "target_module": "metrics_service.py",
            "test_classes": [
                "TestMetricType",
                "TestMetricUnit", 
                "TestMetricValue",
                "TestMetric",
                "TestMetricAlert",
                "TestMetricAggregator",
                "TestMetricCollector",
                "TestSystemMetricsCollector",
                "TestNetworkToolMetricsCollector",
                "TestMetricsService",
                "TestGlobalFunctions",
                "TestComplexScenarios"
            ],
            "test_categories": [
                "Unit Tests",
                "Integration Tests",
                "Edge Cases",
                "Error Handling",
                "Concurrency Tests",
                "Parametrized Tests"
            ]
        },
        "output_files": {
            "html_report": f"result_metrics_service_2025-08-30.html",
            "junit_xml": f"result_metrics_service_2025-08-30.xml",
            "coverage_json": f"result_metrics_service_coverage_2025-08-30.json",
            "coverage_html": f"coverage_metrics_service_2025-08-30/index.html"
        },
        "test_features_covered": [
            "Enum classes (MetricType, MetricUnit)",
            "Dataclasses (MetricValue, Metric, MetricAlert)",
            "Service classes (MetricAggregator, MetricCollector, MetricsService)",
            "Specialized collectors (SystemMetricsCollector, NetworkToolMetricsCollector)",
            "Threading and concurrency",
            "File operations and export",
            "Alert system",
            "Global functions",
            "Error handling and edge cases",
            "Mock data and dependencies"
        ]
    }
    
    # Save summary as JSON
    summary_file = os.path.join(OUTPUT_DIR, f"result_metrics_service_summary_2025-08-30.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
    
    # Generate markdown summary
    markdown_summary = generate_markdown_summary(summary)
    markdown_file = os.path.join(OUTPUT_DIR, f"result_metrics_service_summary_2025-08-30.md")
    with open(markdown_file, 'w', encoding='utf-8') as f:
        f.write(markdown_summary)
    
    print(f"Summary JSON saved to: {summary_file}")
    print(f"Summary Markdown saved to: {markdown_file}")
    
    return summary

def generate_markdown_summary(summary):
    """Generate a markdown summary report."""
    md = f"""# Metrics Service Comprehensive Test Report

## Test Execution Summary
- **Timestamp**: {summary['test_execution']['timestamp']}
- **Test File**: {summary['test_execution']['test_file']}
- **Success**: {'✅ PASSED' if summary['test_execution']['success'] else '❌ FAILED'}
- **Execution Time**: {summary['test_execution']['execution_time_seconds']:.2f} seconds
- **Test Directory**: {summary['test_execution']['test_directory']}

## Coverage Information
- **Target Module**: {summary['test_coverage']['target_module']}
- **Test Classes**: {len(summary['test_coverage']['test_classes'])}
- **Test Categories**: {len(summary['test_coverage']['test_categories'])}

### Test Classes Covered
"""
    
    for test_class in summary['test_coverage']['test_classes']:
        md += f"- {test_class}\n"
    
    md += f"""
### Test Categories
"""
    
    for category in summary['test_coverage']['test_categories']:
        md += f"- {category}\n"
    
    md += f"""
## Output Files Generated
"""
    
    for file_type, filename in summary['output_files'].items():
        md += f"- **{file_type.replace('_', ' ').title()}**: `{filename}`\n"
    
    md += f"""
## Features Tested
"""
    
    for feature in summary['test_features_covered']:
        md += f"- {feature}\n"
    
    md += f"""
## Test Results Analysis

The comprehensive test suite covers:

1. **Core Components**: All main classes and enums
2. **Edge Cases**: Error conditions, invalid inputs, boundary conditions
3. **Integration**: Component interaction and data flow
4. **Concurrency**: Thread safety and parallel operations
5. **Mock Testing**: External dependencies and system calls
6. **Performance**: Memory management and resource cleanup

## Recommendations

1. Review coverage report for any missed code paths
2. Validate all error handling scenarios
3. Check performance metrics for optimization opportunities
4. Ensure all mocked dependencies reflect real behavior

---
*Generated by Comprehensive Test Runner on {summary['test_execution']['timestamp']}*
"""
    
    return md

def validate_outputs():
    """Validate that all expected output files were generated."""
    print("\n" + "="*80)
    print("VALIDATING OUTPUT FILES")
    print("="*80)
    
    expected_files = [
        f"result_metrics_service_2025-08-30.html",
        f"result_metrics_service_2025-08-30.xml",
        f"result_metrics_service_coverage_2025-08-30.json",
        f"result_metrics_service_summary_2025-08-30.json",
        f"result_metrics_service_summary_2025-08-30.md"
    ]
    
    missing_files = []
    existing_files = []
    
    for filename in expected_files:
        filepath = os.path.join(OUTPUT_DIR, filename)
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            existing_files.append(f"{filename} ({file_size:,} bytes)")
            print(f"✅ {filename} - {file_size:,} bytes")
        else:
            missing_files.append(filename)
            print(f"❌ {filename} - NOT FOUND")
    
    # Check coverage HTML directory
    coverage_dir = os.path.join(OUTPUT_DIR, "coverage_metrics_service_2025-08-30")
    if os.path.exists(coverage_dir):
        print(f"✅ Coverage HTML directory - {coverage_dir}")
    else:
        print(f"❌ Coverage HTML directory - NOT FOUND")
        missing_files.append("coverage HTML directory")
    
    if missing_files:
        print(f"\n⚠️  WARNING: {len(missing_files)} expected files are missing:")
        for filename in missing_files:
            print(f"   - {filename}")
    else:
        print(f"\n✅ All {len(expected_files) + 1} expected outputs generated successfully!")
    
    return len(missing_files) == 0

def main():
    """Main execution function."""
    print("METRICS SERVICE COMPREHENSIVE TEST RUNNER")
    print("="*80)
    print(f"Started at: {TIMESTAMP}")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    try:
        # Setup
        setup_environment()
        
        # Run tests
        success, execution_time = run_comprehensive_tests()
        
        # Generate reports
        summary = generate_summary_report(success, execution_time)
        
        # Validate outputs
        outputs_valid = validate_outputs()
        
        # Final status
        print("\n" + "="*80)
        print("FINAL TEST EXECUTION STATUS")
        print("="*80)
        
        if success and outputs_valid:
            print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
            print("✅ Test execution: PASSED")
            print("✅ Output validation: PASSED")
            return_code = 0
        else:
            print("❌ TEST EXECUTION ISSUES DETECTED")
            print(f"❌ Test execution: {'PASSED' if success else 'FAILED'}")
            print(f"❌ Output validation: {'PASSED' if outputs_valid else 'FAILED'}")
            return_code = 1
        
        print(f"\nTotal execution time: {execution_time:.2f} seconds" if execution_time else "")
        print(f"Output directory: {OUTPUT_DIR}")
        print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return return_code
        
    except KeyboardInterrupt:
        print("\n\n❌ Test execution interrupted by user")
        return 130
    except Exception as e:
        print(f"\n\n❌ Unexpected error during test execution: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)