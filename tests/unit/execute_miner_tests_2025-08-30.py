#!/usr/bin/env python3
"""
Enhanced Test Execution Script for miner.py - Version 2
Created: 2025-08-30
Purpose: Comprehensive testing with detailed reporting

Features:
- Standardized output with timestamps
- HTML, JSON, and XML report generation
- Coverage analysis with multiple output formats
- Performance metrics and execution summaries
- Error handling and debugging support
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def execute_comprehensive_tests():
    """Execute comprehensive tests for miner.py with full reporting"""

    # Initialize timing and configuration
    execution_start = datetime.now()
    date_stamp = execution_start.strftime("%Y-%m-%d")
    timestamp_full = execution_start.strftime("%Y-%m-%d_%H-%M-%S")

    # Directory and file setup
    test_directory = Path(__file__).parent
    target_test_file = test_directory / f"test_miner_{date_stamp}.py"

    print("╔" + "═" * 78 + "╗")
    print("║" + "COMPREHENSIVE MINER.PY UNIT TEST EXECUTION".center(78) + "║")
    print("╠" + "═" * 78 + "╣")
    print(
        f"║ Execution Time: {execution_start.strftime('%Y-%m-%d %H:%M:%S')}".ljust(
            79
        )
        + "║"
    )
    print(f"║ Test File: {target_test_file.name}".ljust(79) + "║")
    print(f"║ Target Module: miner.py (PDF Tools)".ljust(79) + "║")
    print("╚" + "═" * 78 + "╝")
    print()

    # Define output file structure following naming convention
    output_files = {
        "html_report": test_directory
        / f"result_miner_{date_stamp}_comprehensive_report.html",
        "json_results": test_directory
        / f"result_miner_{date_stamp}_detailed_results.json",
        "junit_xml": test_directory
        / f"result_miner_{date_stamp}_junit_output.xml",
        "coverage_html_dir": test_directory
        / f"result_miner_{date_stamp}_coverage_html",
        "coverage_json": test_directory
        / f"result_miner_{date_stamp}_coverage_data.json",
        "coverage_xml": test_directory
        / f"result_miner_{date_stamp}_coverage_report.xml",
        "execution_log": test_directory
        / f"result_miner_{date_stamp}_execution_detailed.log",
        "performance_metrics": test_directory
        / f"result_miner_{date_stamp}_performance.json",
        "final_summary": test_directory
        / f"result_miner_{date_stamp}_final_summary.json",
    }

    # Verify test file exists
    if not target_test_file.exists():
        print(f"❌ ERROR: Test file {target_test_file} not found!")
        print(f"   Expected location: {target_test_file}")
        return 1

    print(f"✅ Test file located: {target_test_file}")
    print(f"📁 Output directory: {test_directory}")
    print()

    # Create necessary directories
    output_files["coverage_html_dir"].mkdir(exist_ok=True)

    # Construct comprehensive pytest command
    pytest_command = [
        sys.executable,
        "-m",
        "pytest",
        str(target_test_file),
        # Verbosity and output control
        "--verbose",
        "--tb=short",
        "--capture=no",
        "--show-capture=all",
        # HTML Report Generation
        f'--html={output_files["html_report"]}',
        "--self-contained-html",
        # XML Report for CI/CD integration
        f'--junit-xml={output_files["junit_xml"]}',
        # Coverage Analysis (comprehensive)
        "--cov=miner",
        "--cov-report=term-missing",
        "--cov-report=term:skip-covered",
        f'--cov-report=html:{output_files["coverage_html_dir"]}',
        f'--cov-report=json:{output_files["coverage_json"]}',
        f'--cov-report=xml:{output_files["coverage_xml"]}',
        "--cov-fail-under=75",  # Require 75% coverage
        "--cov-branch",  # Include branch coverage
        # Performance and timing
        "--durations=20",  # Show top 20 slowest tests
        "--durations-min=0.1",  # Only show tests taking more than 0.1s
        # Error handling
        "--maxfail=10",  # Stop after 10 failures
        "--timeout=300",  # 5 minute timeout per test
        # Test discovery and execution
        "--collect-only-quiet",
        "-x",  # Stop on first failure for debugging
        # Warnings
        "--disable-warnings",
        # Additional reporting
        "--tb=line",  # Shorter traceback format
    ]

    print("🚀 EXECUTING PYTEST COMMAND:")
    print("─" * 60)
    print(" ".join(pytest_command))
    print("─" * 60)
    print()

    # Execute the test suite
    try:
        print("⏳ Running test suite...")
        start_time = time.time()

        # Execute with real-time output
        process = subprocess.Popen(
            pytest_command,
            cwd=test_directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )

        # Capture and display output in real-time
        output_lines = []
        while True:
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break
            if output:
                print(output.strip())
                output_lines.append(output)

        return_code = process.poll()
        end_time = time.time()
        execution_duration = end_time - start_time

        # Compile full output
        full_output = "".join(output_lines)

    except subprocess.TimeoutExpired:
        print("❌ ERROR: Test execution timed out after 10 minutes!")
        return 2
    except Exception as e:
        print(f"❌ ERROR: Failed to execute tests: {e}")
        return 3

    # Generate detailed execution log
    execution_end = datetime.now()
    total_duration = execution_end - execution_start

    with open(
        output_files["execution_log"], "w", encoding="utf-8"
    ) as log_file:
        log_file.write("COMPREHENSIVE MINER.PY TEST EXECUTION LOG\\n")
        log_file.write("=" * 80 + "\\n")
        log_file.write(f"Generated: {timestamp_full}\\n")
        log_file.write(f"Target Module: miner.py\\n")
        log_file.write(f"Test File: {target_test_file}\\n")
        log_file.write(f"Test Directory: {test_directory}\\n")
        log_file.write("\\n")

        log_file.write("EXECUTION DETAILS:\\n")
        log_file.write("-" * 40 + "\\n")
        log_file.write(f"Start Time: {execution_start.isoformat()}\\n")
        log_file.write(f"End Time: {execution_end.isoformat()}\\n")
        log_file.write(f"Total Duration: {total_duration}\\n")
        log_file.write(
            f"Test Execution Duration: {execution_duration:.2f} seconds\\n"
        )
        log_file.write(f"Return Code: {return_code}\\n")
        log_file.write(f"Success: {return_code == 0}\\n")
        log_file.write("\\n")

        log_file.write("PYTEST COMMAND:\\n")
        log_file.write("-" * 40 + "\\n")
        log_file.write(" ".join(pytest_command) + "\\n\\n")

        log_file.write("TEST OUTPUT:\\n")
        log_file.write("-" * 40 + "\\n")
        log_file.write(full_output)
        log_file.write("\\n")

        log_file.write("ENVIRONMENT INFO:\\n")
        log_file.write("-" * 40 + "\\n")
        log_file.write(f"Python Version: {sys.version}\\n")
        log_file.write(f"Platform: {sys.platform}\\n")
        log_file.write(f"Working Directory: {os.getcwd()}\\n")
        log_file.write(f"Script Location: {__file__}\\n")

    # Parse coverage data if available
    coverage_summary = {}
    if output_files["coverage_json"].exists():
        try:
            with open(output_files["coverage_json"], "r") as f:
                coverage_data = json.load(f)
                coverage_summary = coverage_data.get("totals", {})
        except Exception as e:
            print(f"⚠️  Warning: Could not parse coverage data: {e}")

    # Generate performance metrics
    performance_data = {
        "execution_time_seconds": execution_duration,
        "total_time_seconds": total_duration.total_seconds(),
        "start_timestamp": execution_start.isoformat(),
        "end_timestamp": execution_end.isoformat(),
        "test_file_size_bytes": target_test_file.stat().st_size,
        "python_version": sys.version_info[:3],
        "platform": sys.platform,
    }

    with open(output_files["performance_metrics"], "w") as f:
        json.dump(performance_data, f, indent=2)

    # Create comprehensive final summary
    summary_data = {
        "metadata": {
            "generated_at": timestamp_full,
            "execution_date": date_stamp,
            "target_module": "miner.py",
            "test_file": str(target_test_file),
            "test_directory": str(test_directory),
            "script_version": "Enhanced Test Runner v2.0",
        },
        "execution_results": {
            "start_time": execution_start.isoformat(),
            "end_time": execution_end.isoformat(),
            "total_duration_formatted": str(total_duration),
            "test_duration_seconds": execution_duration,
            "return_code": return_code,
            "success": return_code == 0,
            "status": "PASSED" if return_code == 0 else "FAILED",
        },
        "generated_outputs": {
            name: {
                "file_path": str(path),
                "exists": path.exists() if path.suffix else path.is_dir(),
                "size_bytes": (
                    path.stat().st_size
                    if (path.exists() and path.is_file())
                    else None
                ),
                "type": "directory" if not path.suffix else "file",
            }
            for name, path in output_files.items()
        },
        "coverage_metrics": coverage_summary,
        "performance_metrics": performance_data,
        "environment": {
            "python_version": sys.version,
            "platform_system": sys.platform,
            "current_directory": os.getcwd(),
            "script_path": __file__,
        },
    }

    # Save final summary
    with open(output_files["final_summary"], "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)

    # Display comprehensive results summary
    print("\\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + "TEST EXECUTION COMPLETED".center(78) + "║")
    print("╠" + "═" * 78 + "╣")
    print(
        f"║ Status: {'✅ SUCCESS' if return_code == 0 else '❌ FAILURE'}".ljust(
            79
        )
        + "║"
    )
    print(f"║ Duration: {total_duration}".ljust(79) + "║")
    print(f"║ Return Code: {return_code}".ljust(79) + "║")
    print("╠" + "═" * 78 + "╣")
    print("║" + "GENERATED REPORTS".center(78) + "║")
    print("╠" + "═" * 78 + "╣")

    for name, path in output_files.items():
        exists = path.exists() if path.suffix else path.is_dir()
        status_icon = "✅" if exists else "❌"
        size_info = ""
        if exists and path.is_file():
            size_kb = path.stat().st_size / 1024
            size_info = f" ({size_kb:.1f} KB)"
        elif exists and path.is_dir():
            size_info = " (directory)"

        display_name = name.replace("_", " ").title()
        line = f"║ {status_icon} {display_name}: {path.name}{size_info}"
        print(line.ljust(79) + "║")

    # Coverage summary display
    if coverage_summary:
        print("╠" + "═" * 78 + "╣")
        print("║" + "COVERAGE SUMMARY".center(78) + "║")
        print("╠" + "═" * 78 + "╣")

        coverage_percent = coverage_summary.get("percent_covered", 0)
        covered_lines = coverage_summary.get("covered_lines", 0)
        total_lines = coverage_summary.get("num_statements", 0)
        missing_lines = coverage_summary.get("missing_lines", 0)

        print(
            f"║ Coverage Percentage: {coverage_percent:.1f}%".ljust(79) + "║"
        )
        print(
            f"║ Lines Covered: {covered_lines}/{total_lines}".ljust(79) + "║"
        )
        print(f"║ Missing Lines: {missing_lines}".ljust(79) + "║")

    print("╚" + "═" * 78 + "╝")

    return return_code


if __name__ == "__main__":
    exit_code = execute_comprehensive_tests()
    print(f"\\n🏁 Test execution completed with exit code: {exit_code}")
    sys.exit(exit_code)
