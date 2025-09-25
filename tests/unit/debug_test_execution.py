#!/usr/bin/env python3
"""
Debug Test Execution - Analyze Import System Issues
Created: 2025-09-08
Purpose: Debug failing tests to identify specific import and configuration issues

This debug version provides detailed error analysis for failed tests.
"""

import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Import our standardized test environment
from test_env_config import setup_test_environment

# Configure logging for debugging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def debug_single_test(test_file: Path) -> dict:
    """Debug a single test file with detailed output.

    Args:
        test_file: Path to the test file

    Returns:
        Dictionary with debug results
    """
    logger.info(f"DEBUG: Analyzing {test_file.name}")

    # Setup environment
    config = setup_test_environment()

    # Try simple pytest execution with maximum verbosity
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(test_file),
        "-v",
        "-s",
        "--tb=long",
        "--disable-warnings",
        "--capture=no",
    ]

    try:
        result = subprocess.run(
            cmd,
            cwd=test_file.parent,
            capture_output=True,
            text=True,
            timeout=60,
        )

        return {
            "test_file": test_file.name,
            "success": result.returncode == 0,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": " ".join(cmd),
        }

    except subprocess.TimeoutExpired:
        return {
            "test_file": test_file.name,
            "success": False,
            "error": "Timeout",
            "return_code": -1,
        }
    except Exception as e:
        return {
            "test_file": test_file.name,
            "success": False,
            "error": str(e),
            "return_code": -2,
        }


def analyze_failed_tests():
    """Analyze the failed tests to understand issues."""
    print("🔍 Debug Analysis - Failed Test Investigation")
    print("=" * 50)

    # Focus on a few key failing tests
    test_files = [
        "test_network_connectivity_simple_2025-08-24.py",
        "test_size_analyzer_config_simplified_2025-08-29.py",
        "test_hub_2025-08-28.py",
    ]

    tests_dir = Path(r"C:\Users\HP1\1_2\tests\unit")

    for test_name in test_files:
        test_path = tests_dir / test_name
        if test_path.exists():
            print(f"\n🧪 Debugging: {test_name}")
            print("-" * 40)

            result = debug_single_test(test_path)

            print(f"Return Code: {result['return_code']}")
            print(f"Success: {result['success']}")

            if result.get("stdout"):
                print("\n📤 STDOUT:")
                print(result["stdout"][-1000:])  # Last 1000 chars

            if result.get("stderr"):
                print("\n📥 STDERR:")
                print(result["stderr"][-1000:])  # Last 1000 chars

            print("\n" + "=" * 50)
        else:
            print(f"❌ Test file not found: {test_name}")


def check_import_issues():
    """Check for specific import issues."""
    print("\n🔍 Import System Analysis")
    print("=" * 30)

    config = setup_test_environment()

    print(f"Python paths configured: {len(config.get('python_paths', []))}")
    print(f"Available modules: {len(config.get('available_modules', []))}")
    print(f"Missing modules: {len(config.get('missing_modules', []))}")

    # Test some common imports that were problematic
    problematic_imports = [
        "rfu.dev_hub",
        "utilities.system.system_cleanup",
        "utilities.network.network_connectivity",
        "PyQt5.QtWidgets",
        "pytest",
    ]

    print("\n📦 Testing Problematic Imports:")
    for module_name in problematic_imports:
        try:
            __import__(module_name)
            print(f"✅ {module_name}")
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
        except Exception as e:
            print(f"⚠️ {module_name}: {e}")


def main():
    """Main debug entry point."""
    check_import_issues()
    analyze_failed_tests()

    print("\n🎯 Next Steps:")
    print("1. Address specific import failures identified above")
    print("2. Update test files to use correct import paths")
    print("3. Install missing dependencies")
    print("4. Re-run tests with fixed imports")


if __name__ == "__main__":
    main()
