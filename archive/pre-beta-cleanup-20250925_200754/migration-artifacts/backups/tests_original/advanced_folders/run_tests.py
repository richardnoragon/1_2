"""Advanced Folders Test Runner.

Provides comprehensive test execution with reporting and coverage analysis.
"""

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional


class TestRunner:
    """Test runner for Advanced Folders module."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.test_dir = project_root / "tests" / "advanced_folders"
        
    def run_unit_tests(self, verbose: bool = False) -> int:
        """Run unit tests only."""
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir),
            "-m", "unit",
            "--tb=short"
        ]
        
        if verbose:
            cmd.append("-v")
            
        return subprocess.call(cmd, cwd=self.project_root)
    
    def run_integration_tests(self, verbose: bool = False) -> int:
        """Run integration tests only."""
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir),
            "-m", "integration",
            "--tb=short"
        ]
        
        if verbose:
            cmd.append("-v")
            
        return subprocess.call(cmd, cwd=self.project_root)
    
    def run_all_tests(self, verbose: bool = False, coverage: bool = True) -> int:
        """Run all tests with optional coverage reporting."""
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir),
            "--tb=short"
        ]
        
        if verbose:
            cmd.append("-v")
            
        if coverage:
            cmd.extend([
                "--cov=src.utilities.advanced_folders",
                "--cov-report=html:htmlcov/advanced_folders",
                "--cov-report=term-missing",
                "--cov-report=xml:coverage_advanced_folders.xml"
            ])
            
        return subprocess.call(cmd, cwd=self.project_root)
    
    def run_performance_tests(self, verbose: bool = False) -> int:
        """Run performance tests only."""
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir),
            "-m", "performance",
            "--tb=short"
        ]
        
        if verbose:
            cmd.append("-v")
            
        return subprocess.call(cmd, cwd=self.project_root)
    
    def run_specific_test(self, test_pattern: str, verbose: bool = False) -> int:
        """Run tests matching a specific pattern."""
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir),
            "-k", test_pattern,
            "--tb=short"
        ]
        
        if verbose:
            cmd.append("-v")
            
        return subprocess.call(cmd, cwd=self.project_root)
    
    def validate_test_environment(self) -> bool:
        """Validate that the test environment is properly set up."""
        # Check if test directory exists
        if not self.test_dir.exists():
            print(f"Error: Test directory not found: {self.test_dir}")
            return False
            
        # Check if conftest.py exists
        conftest_path = self.test_dir / "conftest.py"
        if not conftest_path.exists():
            print(f"Error: conftest.py not found: {conftest_path}")
            return False
            
        # Check if pytest is available
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pytest", "--version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except subprocess.CalledProcessError:
            print("Error: pytest not available. Install with: pip install pytest")
            return False
            
        # Check if source modules can be imported
        try:
            import src.utilities.advanced_folders
            print("✓ Advanced Folders modules can be imported")
        except ImportError as e:
            print(f"Error: Cannot import Advanced Folders modules: {e}")
            return False
            
        print("✓ Test environment validation passed")
        return True
    
    def generate_test_report(self, output_file: Optional[Path] = None) -> int:
        """Generate comprehensive test report."""
        if output_file is None:
            output_file = self.project_root / "test_report_advanced_folders.html"
            
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_dir),
            "--html=" + str(output_file),
            "--self-contained-html",
            "--tb=short",
            "--cov=src.utilities.advanced_folders",
            "--cov-report=html:htmlcov/advanced_folders"
        ]
        
        result = subprocess.call(cmd, cwd=self.project_root)
        
        if result == 0:
            print(f"✓ Test report generated: {output_file}")
            print(f"✓ Coverage report: {self.project_root}/htmlcov/advanced_folders/index.html")
        
        return result


def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(description="Advanced Folders Test Runner")
    parser.add_argument(
        "--test-type",
        choices=["unit", "integration", "performance", "all"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Disable coverage reporting"
    )
    parser.add_argument(
        "--pattern", "-k",
        help="Run tests matching specific pattern"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate HTML test report"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate test environment only"
    )
    
    args = parser.parse_args()
    
    # Find project root
    current_dir = Path(__file__).parent
    project_root = current_dir
    while project_root.parent != project_root:
        if (project_root / "src").exists():
            break
        project_root = project_root.parent
    else:
        print("Error: Could not find project root directory")
        return 1
    
    runner = TestRunner(project_root)
    
    # Validate environment first
    if not runner.validate_test_environment():
        return 1
    
    if args.validate:
        print("Test environment validation completed successfully")
        return 0
    
    # Run tests based on arguments
    if args.pattern:
        result = runner.run_specific_test(args.pattern, args.verbose)
    elif args.test_type == "unit":
        result = runner.run_unit_tests(args.verbose)
    elif args.test_type == "integration":
        result = runner.run_integration_tests(args.verbose)
    elif args.test_type == "performance":
        result = runner.run_performance_tests(args.verbose)
    else:  # all
        result = runner.run_all_tests(args.verbose, not args.no_coverage)
    
    # Generate report if requested
    if args.report:
        runner.generate_test_report()
    
    return result


if __name__ == "__main__":
    sys.exit(main())