#!/usr/bin/env python3
"""
Test Runner for network_base.py Unit Tests
Generated on: 2025-08-29
Execution timestamp will be included in all outputs
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_network_base_tests():
    """Run comprehensive unit tests for network_base.py with detailed reporting."""
    
    # Get current timestamp
    timestamp = datetime.now()
    print(f"\n{'='*80}")
    print(f"NETWORK_BASE.PY UNIT TEST EXECUTION")
    print(f"Started at: {timestamp.isoformat()}")
    print(f"{'='*80}")
    
    # Set up paths
    project_root = Path(__file__).parent
    test_dir = project_root / "tests" / "unit"
    test_file = test_dir / "test_network_base_2025-08-29.py"
    
    # Ensure test directory exists
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Get Python executable path
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        # We're in a virtual environment
        if os.name == 'nt':  # Windows
            python_exe = Path(sys.executable)
        else:  # Unix/Linux/Mac
            python_exe = Path(sys.executable)
    else:
        python_exe = Path(sys.executable)
    
    # Prepare pytest command
    pytest_cmd = [
        str(python_exe), "-m", "pytest",
        str(test_file),
        "--verbose",
        "--tb=short",
        "--html=" + str(test_dir / f"result_network_base_2025-08-29.html"),
        "--self-contained-html",
        "--json-report",
        "--json-report-file=" + str(test_dir / f"result_network_base_2025-08-29.json"),
        "--cov=src.utilities.network.network_connectivity_complex.core.network_base",
        "--cov-report=html:" + str(test_dir / f"result_network_base_coverage_2025-08-29"),
        "--cov-report=json:" + str(test_dir / f"result_network_base_coverage_2025-08-29.json"),
        "--cov-report=term-missing",
        "--durations=10",
        "--color=yes"
    ]
    
    print(f"Executing: {' '.join(pytest_cmd)}")
    print(f"Working directory: {project_root}")
    print(f"Test file: {test_file}")
    print(f"\n{'-'*80}")
    
    try:
        # Run pytest
        result = subprocess.run(
            pytest_cmd,
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        # Print output
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        # Generate summary report
        generate_summary_report(test_dir, timestamp, result.returncode)
        
        end_timestamp = datetime.now()
        duration = end_timestamp - timestamp
        
        print(f"\n{'-'*80}")
        print(f"Test execution completed at: {end_timestamp.isoformat()}")
        print(f"Total duration: {duration.total_seconds():.2f} seconds")
        print(f"Exit code: {result.returncode}")
        
        if result.returncode == 0:
            print("✅ ALL TESTS PASSED")
        else:
            print("❌ SOME TESTS FAILED")
        
        print(f"{'='*80}")
        
        return result.returncode
        
    except subprocess.TimeoutExpired:
        print("❌ Test execution timed out after 5 minutes")
        return 1
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1

def generate_summary_report(test_dir, start_time, exit_code):
    """Generate a comprehensive summary report."""
    
    summary_file = test_dir / f"result_network_base_summary_2025-08-29.json"
    
    summary_data = {
        "test_execution_summary": {
            "target_module": "network_base.py",
            "test_framework": "pytest",
            "execution_timestamp": start_time.isoformat(),
            "test_file": "test_network_base_2025-08-29.py",
            "exit_code": exit_code,
            "status": "PASSED" if exit_code == 0 else "FAILED"
        },
        "generated_reports": [
            "result_network_base_2025-08-29.html",
            "result_network_base_2025-08-29.json", 
            "result_network_base_coverage_2025-08-29.json",
            "result_network_base_coverage_2025-08-29/index.html"
        ],
        "test_specifications": {
            "coverage_target": "All functions and methods in network_base.py",
            "test_types": [
                "Unit tests",
                "Edge cases", 
                "Error scenarios",
                "Threading safety",
                "Mock integration"
            ],
            "assertions_included": [
                "Initialization testing",
                "Method functionality",
                "Error handling",
                "State management",
                "Callback systems",
                "Configuration management",
                "Data storage and retrieval",
                "Threading operations"
            ]
        }
    }
    
    # Try to read pytest JSON report for additional details
    pytest_json_file = test_dir / f"result_network_base_2025-08-29.json"
    if pytest_json_file.exists():
        try:
            with open(pytest_json_file, 'r') as f:
                pytest_data = json.load(f)
                summary_data["pytest_summary"] = {
                    "total_tests": pytest_data.get("summary", {}).get("total", 0),
                    "passed": pytest_data.get("summary", {}).get("passed", 0),
                    "failed": pytest_data.get("summary", {}).get("failed", 0),
                    "skipped": pytest_data.get("summary", {}).get("skipped", 0),
                    "duration": pytest_data.get("duration", 0)
                }
        except Exception as e:
            summary_data["pytest_summary"] = {"error": f"Could not parse pytest JSON: {e}"}
    
    # Write summary
    with open(summary_file, 'w') as f:
        json.dump(summary_data, f, indent=2)
    
    print(f"\n📊 Summary report generated: {summary_file}")

if __name__ == "__main__":
    exit_code = run_network_base_tests()
    sys.exit(exit_code)