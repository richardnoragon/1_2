"""
Test runner for Advanced Folders unit tests.

Provides comprehensive test execution with coverage reporting,
performance measurement, and detailed result analysis.
"""

import sys
import time
from pathlib import Path
from typing import Any, Dict

import pytest


def run_unit_tests(
    test_pattern: str = "test_*.py",
    coverage: bool = True,
    verbose: bool = True,
    stop_on_first_failure: bool = False
) -> Dict[str, Any]:
    """
    Run unit tests for Advanced Folders components.
    
    Args:
        test_pattern: Pattern to match test files
        coverage: Whether to generate coverage report
        verbose: Whether to use verbose output
        stop_on_first_failure: Whether to stop on first failure
        
    Returns:
        Dictionary with test results and statistics
    """
    # Build pytest arguments
    args = []
    
    # Add test directory
    test_dir = Path(__file__).parent / "unit"
    args.append(str(test_dir))
    
    # Add pattern filter
    args.extend(["-k", test_pattern.replace("test_", "").replace(".py", "")])
    
    # Add verbosity
    if verbose:
        args.append("-v")
    
    # Add stop on first failure
    if stop_on_first_failure:
        args.append("-x")
    
    # Add coverage if requested
    if coverage:
        args.extend([
            "--cov=src.rfu.advanced_folders",
            "--cov-report=html:tests/coverage_html",
            "--cov-report=term-missing",
            "--cov-fail-under=90"
        ])
    
    # Add markers for categorization
    args.extend([
        "-m", "unit",
        "--tb=short"
    ])
    
    print(f"Running unit tests with arguments: {' '.join(args)}")
    print("=" * 70)
    
    # Record start time
    start_time = time.time()
    
    # Run tests
    exit_code = pytest.main(args)
    
    # Record end time
    end_time = time.time()
    duration = end_time - start_time
    
    # Analyze results
    results = {
        "exit_code": exit_code,
        "duration_seconds": duration,
        "success": exit_code == 0,
        "coverage_enabled": coverage,
        "test_directory": str(test_dir),
        "pytest_args": args
    }
    
    print("=" * 70)
    print(f"Unit tests completed in {duration:.2f} seconds")
    success_text = 'SUCCESS' if exit_code == 0 else 'FAILURE'
    print(f"Exit code: {exit_code} ({success_text})")
    
    if coverage:
        print("Coverage report generated in tests/coverage_html/")
    
    return results


def run_specific_test_class(test_file: str, test_class: str) -> Dict[str, Any]:
    """
    Run a specific test class.
    
    Args:
        test_file: Name of test file (e.g., "test_models")
        test_class: Name of test class (e.g., "TestFolderConfiguration")
        
    Returns:
        Dictionary with test results
    """
    test_dir = Path(__file__).parent / "unit"
    test_path = test_dir / f"{test_file}.py"
    
    if not test_path.exists():
        return {
            "success": False,
            "error": f"Test file not found: {test_path}"
        }
    
    # Build pytest arguments
    args = [
        str(test_path) + f"::{test_class}",
        "-v",
        "--tb=short"
    ]
    
    print(f"Running specific test class: {test_class} in {test_file}")
    print("=" * 50)
    
    start_time = time.time()
    exit_code = pytest.main(args)
    end_time = time.time()
    
    results = {
        "exit_code": exit_code,
        "duration_seconds": end_time - start_time,
        "success": exit_code == 0,
        "test_file": test_file,
        "test_class": test_class
    }
    
    print("=" * 50)
    print(f"Test class completed in {results['duration_seconds']:.2f} seconds")
    
    return results


def run_performance_tests() -> Dict[str, Any]:
    """
    Run performance-focused tests.
    
    Returns:
        Dictionary with performance test results
    """
    test_dir = Path(__file__).parent / "unit"
    
    args = [
        str(test_dir),
        "-m", "performance",
        "-v",
        "--tb=short",
        "--durations=10"  # Show 10 slowest tests
    ]
    
    print("Running performance tests...")
    print("=" * 50)
    
    start_time = time.time()
    exit_code = pytest.main(args)
    end_time = time.time()
    
    return {
        "exit_code": exit_code,
        "duration_seconds": end_time - start_time,
        "success": exit_code == 0,
        "test_type": "performance"
    }


def run_validation_tests() -> Dict[str, Any]:
    """
    Run validation-focused tests.
    
    Returns:
        Dictionary with validation test results
    """
    test_dir = Path(__file__).parent / "unit"
    
    args = [
        str(test_dir),
        "-k", "validation",
        "-v",
        "--tb=short"
    ]
    
    print("Running validation tests...")
    print("=" * 50)
    
    start_time = time.time()
    exit_code = pytest.main(args)
    end_time = time.time()
    
    return {
        "exit_code": exit_code,
        "duration_seconds": end_time - start_time,
        "success": exit_code == 0,
        "test_type": "validation"
    }


def run_database_tests() -> Dict[str, Any]:
    """
    Run database-focused tests.
    
    Returns:
        Dictionary with database test results
    """
    test_dir = Path(__file__).parent / "unit"
    
    args = [
        str(test_dir),
        "-k", "repository or database",
        "-v",
        "--tb=short"
    ]
    
    print("Running database tests...")
    print("=" * 50)
    
    start_time = time.time()
    exit_code = pytest.main(args)
    end_time = time.time()
    
    return {
        "exit_code": exit_code,
        "duration_seconds": end_time - start_time,
        "success": exit_code == 0,
        "test_type": "database"
    }


def run_comprehensive_test_suite() -> Dict[str, Any]:
    """
    Run comprehensive test suite with all categories.
    
    Returns:
        Dictionary with comprehensive test results
    """
    print("=" * 70)
    print("ADVANCED FOLDERS - COMPREHENSIVE UNIT TEST SUITE")
    print("=" * 70)
    
    overall_start = time.time()
    all_results = []
    
    # Test categories to run
    test_categories = [
        ("Exceptions", lambda: run_specific_test_class("test_exceptions", "")),
        ("Validation", run_validation_tests),
        ("Models", lambda: run_specific_test_class("test_models", "")),
        ("Repository", run_database_tests),
        ("Error Handling", lambda: run_specific_test_class("test_error_handling", "")),
        ("Performance", run_performance_tests)
    ]
    
    success_count = 0
    
    for category_name, test_func in test_categories:
        print(f"\n{'='*20} {category_name} Tests {'='*20}")
        
        try:
            result = test_func()
            result["category"] = category_name
            all_results.append(result)
            
            if result["success"]:
                success_count += 1
                print(f"✓ {category_name} tests PASSED")
            else:
                print(f"✗ {category_name} tests FAILED")
                
        except Exception as e:
            print(f"✗ {category_name} tests ERROR: {str(e)}")
            all_results.append({
                "category": category_name,
                "success": False,
                "error": str(e),
                "duration_seconds": 0
            })
    
    overall_end = time.time()
    overall_duration = overall_end - overall_start
    
    # Summary
    total_categories = len(test_categories)
    print(f"\n{'='*70}")
    print("COMPREHENSIVE TEST SUITE SUMMARY")
    print("=" * 70)
    print(f"Total Categories: {total_categories}")
    print(f"Successful: {success_count}")
    print(f"Failed: {total_categories - success_count}")
    print(f"Total Duration: {overall_duration:.2f} seconds")
    print(f"Overall Result: {'SUCCESS' if success_count == total_categories else 'FAILURE'}")
    
    return {
        "overall_success": success_count == total_categories,
        "total_categories": total_categories,
        "successful_categories": success_count,
        "failed_categories": total_categories - success_count,
        "total_duration_seconds": overall_duration,
        "category_results": all_results
    }


if __name__ == "__main__":
    """Command-line interface for test runner."""
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "all":
            run_comprehensive_test_suite()
        elif command == "unit":
            run_unit_tests()
        elif command == "performance":
            run_performance_tests()
        elif command == "validation":
            run_validation_tests()
        elif command == "database":
            run_database_tests()
        elif command == "coverage":
            run_unit_tests(coverage=True, verbose=True)
        else:
            print(f"Unknown command: {command}")
            print("Available commands: all, unit, performance, validation, database, coverage")
    else:
        # Default: run comprehensive suite
        run_comprehensive_test_suite()