"""
Test Execution Script for dev_hub.py
Generated on: 2025-08-28

This script runs comprehensive unit tests for dev_hub.py with detailed reporting.
"""

import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def setup_environment():
    """Set up the test environment."""
    print("🔧 Setting up test environment...")
    
    # Ensure we're in the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir.parent.parent)
    
    # Add source directory to Python path
    src_dir = Path.cwd() / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    
    print(f"✅ Working directory: {Path.cwd()}")
    print(f"✅ Source directory added: {src_dir}")


def get_python_executable():
    """Get the correct Python executable path."""
    # Use the virtual environment Python if available
    venv_python = Path.cwd() / "venv" / "Scripts" / "python.exe"
    if venv_python.exists():
        return str(venv_python)
    
    # Fallback to system Python
    return sys.executable


def run_tests():
    """Execute the test suite with comprehensive reporting."""
    print("🧪 Starting comprehensive test execution...")
    
    start_time = datetime.now()
    python_exe = get_python_executable()
    
    # Test command with comprehensive reporting
    test_cmd = [
        python_exe, "-m", "pytest",
        "tests/unit/test_dev_hub_2025-08-28.py",
        "-v",
        "--tb=long",
        "--strict-markers",
        "--color=yes",
        "--durations=10",
        f"--html=tests/unit/result_dev_hub_2025-08-28.html",
        "--self-contained-html",
        "--json-report",
        f"--json-report-file=tests/unit/result_dev_hub_2025-08-28.json",
        "--cov=src.rfu.dev_hub",
        f"--cov-report=html:tests/unit/result_dev_hub_coverage_2025-08-28",
        f"--cov-report=json:tests/unit/result_dev_hub_coverage_2025-08-28.json",
        "--cov-report=term-missing",
        "--cov-report=term:skip-covered",
        "--maxfail=5"
    ]
    
    print(f"📋 Executing command: {' '.join(test_cmd)}")
    print("=" * 80)
    
    try:
        # Run the tests
        result = subprocess.run(
            test_cmd,
            capture_output=False,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        end_time = datetime.now()
        execution_time = end_time - start_time
        
        print("=" * 80)
        print(f"⏱️  Total execution time: {execution_time}")
        print(f"🔄 Exit code: {result.returncode}")
        
        # Generate summary
        generate_test_summary(start_time, end_time, result.returncode)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Test execution timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Error during test execution: {e}")
        return False


def generate_test_summary(start_time, end_time, exit_code):
    """Generate a test execution summary."""
    summary = {
        "test_execution_summary": {
            "target_module": "dev_hub.py",
            "test_file": "test_dev_hub_2025-08-28.py",
            "execution_date": "2025-08-28",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": (end_time - start_time).total_seconds(),
            "exit_code": exit_code,
            "success": exit_code == 0,
            "reports_generated": [
                "result_dev_hub_2025-08-28.html",
                "result_dev_hub_2025-08-28.json",
                "result_dev_hub_coverage_2025-08-28/index.html",
                "result_dev_hub_coverage_2025-08-28.json"
            ]
        }
    }
    
    # Write summary to file
    summary_file = Path("tests/unit/result_dev_hub_execution_summary_2025-08-28.json")
    
    try:
        import json
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"📊 Test summary saved to: {summary_file}")
    except Exception as e:
        print(f"⚠️  Could not save test summary: {e}")


def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    # Map package names to their import names
    required_packages = {
        'pytest': 'pytest',
        'pytest-html': 'pytest_html',
        'pytest-json-report': 'pytest_jsonreport',
        'pytest-cov': 'pytest_cov',
        'pytest-mock': 'pytest_mock'
    }
    
    missing_packages = []
    
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("💡 Install with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All required packages are installed")
    return True


def main():
    """Main execution function."""
    print("🚀 Dev Hub Test Execution Script")
    print("=" * 50)
    print(f"📅 Date: 2025-08-28")
    print("🎯 Target: dev_hub.py")
    print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 50)
    
    # Setup environment
    setup_environment()
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Dependency check failed. Exiting.")
        return 1
    
    # Run tests
    success = run_tests()
    
    # Final status
    if success:
        print("\n🎉 Test execution completed successfully!")
        print("📁 Check the tests/unit/ directory for detailed reports:")
        print("   • HTML Report: result_dev_hub_2025-08-28.html")
        print("   • JSON Report: result_dev_hub_2025-08-28.json")
        print("   • Coverage Report: result_dev_hub_coverage_2025-08-28/")
        return 0
    else:
        print("\n❌ Test execution failed!")
        print("📋 Check the output above for error details")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)