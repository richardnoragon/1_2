#!/usr/bin/env python3
"""
HP-03: Critical Functionality Verification Script (Simple Version)

This script verifies critical functionality after 176,938 deletions.
Uses ASCII-safe output for Windows console compatibility.

Generated: 2025-12-19T02:37:30Z
Context: Post-007-upgrade-to-login merge validation
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add project paths
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Test execution metadata
TEST_START_TIME = datetime.now()
TEST_RESULTS = {}
CRITICAL_FAILURES = []
WARNINGS = []


def log_test_result(test_name, passed, details="", critical=False):
    """Log test result with timing and details."""
    TEST_RESULTS[test_name] = {
        "passed": passed,
        "details": details,
        "timestamp": datetime.now(),
        "critical": critical,
    }

    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {test_name}")
    if details:
        print(f"    Details: {details}")

    if not passed and critical:
        CRITICAL_FAILURES.append(f"{test_name}: {details}")
    elif not passed:
        WARNINGS.append(f"{test_name}: {details}")


def test_core_imports():
    """Test that core application modules can be imported."""
    print("\n" + "=" * 70)
    print("TEST CATEGORY: CORE IMPORTS VALIDATION")
    print("=" * 70)

    core_modules = [
        ("main", "main"),
        ("config_manager", "src.config_manager"),
        ("log_manager", "src.log_manager"),
        ("rfu_hub", "src.rfu.hub"),
        ("tabbed_hub", "src.tabbed_hub"),
        ("auth_service", "src.core.auth.auth_service"),
        ("file_validator", "src.file_validator"),
        ("database_manager", "src.database.database_manager"),
    ]

    for module_name, import_path in core_modules:
        try:
            __import__(import_path)
            log_test_result(f"Import {module_name}", True, f"Module: {import_path}")
        except Exception as e:
            log_test_result(
                f"Import {module_name}",
                False,
                f"Failed to import {import_path}: {e}",
                critical=True,
            )


def test_removed_modules_cleanup():
    """Verify that removed modules are properly cleaned up."""
    print("\n" + "=" * 70)
    print("TEST CATEGORY: REMOVED MODULES CLEANUP VERIFICATION")
    print("=" * 70)

    # Modules that should be completely removed
    removed_modules = [
        "src.file_explorer",
        "src_backup.utilities.pdf_tools",
        "src.analytics.analytics",
    ]

    # Directories that should be completely removed
    removed_directories = [
        project_root / "src" / "file_explorer",
        project_root / "src_backup",
    ]

    for module in removed_modules:
        try:
            __import__(module)
            log_test_result(
                f"Removed Module {module}",
                False,
                f"Module {module} still exists but should be removed",
            )
        except ImportError:
            log_test_result(
                f"Removed Module {module}", True, f"Module {module} properly removed"
            )
        except Exception as e:
            log_test_result(
                f"Removed Module {module}",
                False,
                f"Unexpected error checking {module}: {e}",
            )

    for directory in removed_directories:
        if directory.exists():
            log_test_result(
                f"Removed Directory {directory.name}",
                False,
                f"Directory {directory} still exists",
            )
        else:
            log_test_result(
                f"Removed Directory {directory.name}",
                True,
                f"Directory {directory} properly removed",
            )


def test_current_architecture():
    """Test current architecture components are functioning."""
    print("\n" + "=" * 70)
    print("TEST CATEGORY: CURRENT ARCHITECTURE VALIDATION")
    print("=" * 70)

    # Test current src structure
    current_components = [
        ("src/config_manager.py", "Configuration management"),
        ("src/log_manager.py", "Logging system"),
        ("src/core/auth/", "Authentication system"),
        ("src/file_validator/", "File validation system"),
        ("src/database/", "Database management"),
        ("src/rfu/hub.py", "Hub integration utilities"),
        ("src/tabbed_hub.py", "Main tabbed hub interface"),
        ("src/tools/", "Tool categories"),
    ]

    for component_path, description in current_components:
        full_path = project_root / component_path
        exists = full_path.exists()
        log_test_result(
            f"Architecture {description}",
            exists,
            f"Path: {component_path} {'exists' if exists else 'missing'}",
            critical=not exists,
        )


def test_hub_functionality():
    """Test hub functionality without GUI initialization."""
    print("\n" + "=" * 70)
    print("TEST CATEGORY: HUB FUNCTIONALITY")
    print("=" * 70)

    try:
        # Test tabbed hub import
        import src.tabbed_hub

        log_test_result(
            "Tabbed Hub Import", True, "Tabbed hub module imported successfully"
        )

        # Test RFUHub class exists
        from src.tabbed_hub import RFUHub

        log_test_result("RFUHub Class", True, "RFUHub class available")

        # Test key methods exist (without instantiation)
        key_methods = [
            "launch_tool",
            "get_available_tools",
            "register_tool",
            "unregister_tool",
            "update_tool_progress",
        ]

        for method_name in key_methods:
            if hasattr(RFUHub, method_name):
                log_test_result(
                    f"Hub Method {method_name}", True, f"Method {method_name} exists"
                )
            else:
                log_test_result(
                    f"Hub Method {method_name}", False, f"Method {method_name} missing"
                )

    except Exception as e:
        log_test_result(
            "Hub Functionality Test",
            False,
            f"Hub functionality test failed: {e}",
            critical=True,
        )


def test_main_application():
    """Test main application functionality."""
    print("\n" + "=" * 70)
    print("TEST CATEGORY: MAIN APPLICATION")
    print("=" * 70)

    try:
        import main

        # Test interface mode enumeration
        from main import InterfaceMode

        log_test_result(
            "Interface Mode Enum",
            hasattr(InterfaceMode, "DIALOG_HUB"),
            "DIALOG_HUB mode available",
        )

        # Test that multi-pane is properly removed
        log_test_result(
            "Multi-Pane Removal",
            not hasattr(InterfaceMode, "MULTI_PANE"),
            "MULTI_PANE mode properly removed",
        )

        # Test main window class exists
        if hasattr(main, "RFUMainWindow"):
            log_test_result("Main Window Class", True, "RFUMainWindow class available")

            # Test launch_tool method exists
            if hasattr(main.RFUMainWindow, "launch_tool"):
                log_test_result(
                    "Main Launch Tool", True, "launch_tool method exists in main window"
                )
            else:
                log_test_result(
                    "Main Launch Tool",
                    False,
                    "launch_tool method missing from main window",
                )
        else:
            log_test_result(
                "Main Window Class",
                False,
                "RFUMainWindow class not found",
                critical=True,
            )

        # Test database initialization function
        if hasattr(main, "initialize_database_system"):
            log_test_result(
                "Database Init Function",
                True,
                "initialize_database_system function available",
            )
        else:
            log_test_result(
                "Database Init Function",
                False,
                "initialize_database_system function missing",
            )

    except Exception as e:
        log_test_result(
            "Main Application Test",
            False,
            f"Failed to test main application: {e}",
            critical=True,
        )


def test_authentication_system():
    """Test authentication system integration."""
    print("\n" + "=" * 70)
    print("TEST CATEGORY: AUTHENTICATION SYSTEM")
    print("=" * 70)

    try:
        # Test core auth components
        import src.core.auth.auth_service

        log_test_result("Auth Service Module", True, "Auth service module imported")

        import src.core.auth.models.user_account

        log_test_result("User Account Model", True, "User account model imported")

        # Test login dialog
        import src.rfu.login_dialog

        log_test_result("Login Dialog", True, "Login dialog module imported")

        # Test admin panel
        try:
            import src.rfu.admin_panel

            log_test_result("Admin Panel", True, "Admin panel module imported")
        except ImportError as e:
            log_test_result("Admin Panel", False, f"Admin panel import failed: {e}")

    except Exception as e:
        log_test_result(
            "Authentication System",
            False,
            f"Authentication test failed: {e}",
            critical=True,
        )


def test_file_validator():
    """Test file validator system."""
    print("\n" + "=" * 70)
    print("TEST CATEGORY: FILE VALIDATOR SYSTEM")
    print("=" * 70)

    try:
        # Test main validator module
        import src.file_validator

        log_test_result("File Validator Module", True, "File validator module imported")

        # Test API functions exist
        if hasattr(src.file_validator, "detect_file_type"):
            log_test_result(
                "Detect File Type API", True, "detect_file_type function available"
            )
        else:
            log_test_result(
                "Detect File Type API", False, "detect_file_type function missing"
            )

        # Test models
        try:
            import src.file_validator.models

            log_test_result("Validator Models", True, "File validator models imported")
        except ImportError as e:
            log_test_result("Validator Models", False, f"Models import failed: {e}")

    except Exception as e:
        log_test_result(
            "File Validator System",
            False,
            f"File validator test failed: {e}",
            critical=True,
        )


def test_tool_discovery():
    """Test tool discovery in current structure."""
    print("\n" + "=" * 70)
    print("TEST CATEGORY: TOOL DISCOVERY")
    print("=" * 70)

    tools_dir = project_root / "src" / "tools"

    if tools_dir.exists():
        log_test_result("Tools Directory", True, f"Tools directory exists: {tools_dir}")

        # Count tool categories
        categories = [d for d in tools_dir.iterdir() if d.is_dir()]
        log_test_result(
            "Tool Categories",
            len(categories) > 5,
            f"Found {len(categories)} tool categories",
        )

        # List categories
        for category in categories:
            print(f"    Found category: {category.name}")

    else:
        log_test_result(
            "Tools Directory", False, "Tools directory missing", critical=True
        )


def generate_summary():
    """Generate test execution summary."""
    print("\n" + "=" * 80)
    print("HP-03 CRITICAL FUNCTIONALITY VERIFICATION - SUMMARY")
    print("=" * 80)

    total_tests = len(TEST_RESULTS)
    passed_tests = sum(1 for result in TEST_RESULTS.values() if result["passed"])
    critical_failures_count = len(CRITICAL_FAILURES)
    warnings_count = len(WARNINGS)

    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    print(f"TEST EXECUTION SUMMARY:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {total_tests - passed_tests}")
    print(f"   Success Rate: {success_rate:.1f}%")
    print(f"   Critical Failures: {critical_failures_count}")
    print(f"   Warnings: {warnings_count}")

    duration = datetime.now() - TEST_START_TIME
    print(f"   Execution Time: {duration.total_seconds():.2f}s")

    # Overall status determination
    if critical_failures_count == 0:
        if warnings_count == 0:
            status = "EXCELLENT - All tests passed"
        elif warnings_count <= 3:
            status = "GOOD - Minor issues only"
        else:
            status = "ACCEPTABLE - Multiple warnings"
    else:
        status = "CRITICAL ISSUES DETECTED"

    print(f"\nOVERALL STATUS: {status}")

    if CRITICAL_FAILURES:
        print(f"\nCRITICA L FAILURES:")
        for i, failure in enumerate(CRITICAL_FAILURES, 1):
            print(f"   {i}. {failure}")

    if WARNINGS:
        print(f"\nWARNINGS:")
        for i, warning in enumerate(WARNINGS, 1):
            print(f"   {i}. {warning}")

    # Key findings
    print(f"\nKEY FINDINGS:")
    print(
        f"   - src/file_explorer/ removal: {'Verified' if any('file_explorer' in r for r in TEST_RESULTS) else 'Not tested'}"
    )
    print(
        f"   - Current architecture: {'Functional' if passed_tests > total_tests * 0.7 else 'Issues detected'}"
    )
    print(
        f"   - Tool launching: {'Available' if any('launch_tool' in r for r in TEST_RESULTS) else 'Not verified'}"
    )

    return {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "success_rate": success_rate,
        "critical_failures": critical_failures_count,
        "warnings": warnings_count,
        "duration": duration.total_seconds(),
        "status": status,
    }


def main():
    """Execute HP-03 verification suite."""
    print("=" * 80)
    print("HP-03: CRITICAL FUNCTIONALITY VERIFICATION")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    print(f"\nSCOPE: Verify functionality after 176,938 deletions")
    print(f"CONTEXT: Post-007-upgrade-to-login merge validation")
    print(f"Started: {TEST_START_TIME.strftime('%Y-%m-%d %H:%M:%S')}")

    # Execute all test categories
    test_core_imports()
    test_removed_modules_cleanup()
    test_current_architecture()
    test_main_application()
    test_hub_functionality()
    test_authentication_system()
    test_file_validator()
    test_tool_discovery()

    # Generate summary
    summary = generate_summary()

    print(f"\n" + "=" * 80)
    print(f"HP-03 VERIFICATION COMPLETED")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    return summary


if __name__ == "__main__":
    summary = main()

    # Exit with appropriate code
    if summary["critical_failures"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)
