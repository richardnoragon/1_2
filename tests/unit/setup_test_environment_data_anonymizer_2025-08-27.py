#!/usr/bin/env python3
"""
Test Environment Setup Script for Data Anonymizer Unit Tests

Script: setup_test_environment_data_anonymizer_2025-08-27.py
Created: 2025-08-27
Purpose: Setup and configure the testing environment for data_anonymizer.py

This script:
1. Installs required testing dependencies
2. Configures the Python environment
3. Validates the test setup
4. Provides guidance for running tests
"""

import os
import platform
import subprocess
import sys
from pathlib import Path


class TestEnvironmentSetup:
    """Setup and configuration for the test environment."""

    def __init__(self):
        """Initialize the setup manager."""
        self.script_dir = Path(__file__).parent
        self.project_root = self.script_dir.parent.parent
        self.requirements_file = (
            self.script_dir
            / "requirements_test_data_anonymizer_2025-08-27.txt"
        )

    def check_python_version(self):
        """Check if Python version is compatible."""
        print("Checking Python version...")

        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 7):
            print(
                f"ERROR: Python 3.7 or higher is required. Current: {version.major}.{version.minor}"
            )
            return False

        print(
            f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible"
        )
        return True

    def check_pip_availability(self):
        """Check if pip is available."""
        print("Checking pip availability...")

        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                check=True,
                capture_output=True,
            )
            print("✓ pip is available")
            return True
        except subprocess.CalledProcessError:
            print("ERROR: pip is not available")
            return False

    def install_dependencies(self):
        """Install required testing dependencies."""
        print(f"Installing dependencies from {self.requirements_file}...")

        if not self.requirements_file.exists():
            print(
                f"ERROR: Requirements file not found: {self.requirements_file}"
            )
            return False

        try:
            # Upgrade pip first
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                check=True,
            )

            # Install requirements
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    str(self.requirements_file),
                ],
                check=True,
            )

            print("✓ Dependencies installed successfully")
            return True

        except subprocess.CalledProcessError as e:
            print(f"ERROR: Failed to install dependencies: {e}")
            return False

    def validate_imports(self):
        """Validate that required modules can be imported."""
        print("Validating installed packages...")

        required_modules = [
            "pytest",
            "pytest_cov",
            "pytest_html",
            "pytest_json_report",
            "pytest_mock",
            "coverage",
            "PyQt5",
        ]

        failed_imports = []

        for module in required_modules:
            try:
                __import__(module)
                print(f"✓ {module}")
            except ImportError:
                failed_imports.append(module)
                print(f"✗ {module}")

        if failed_imports:
            print(f"ERROR: Failed to import: {', '.join(failed_imports)}")
            return False

        print("✓ All required modules are available")
        return True

    def setup_environment_variables(self):
        """Setup necessary environment variables."""
        print("Setting up environment variables...")

        env_vars = {
            "PYTHONPATH": str(self.project_root),
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
            "PYTEST_TIMEOUT": "300",
        }

        for var, value in env_vars.items():
            os.environ[var] = value
            print(f"✓ {var} = {value}")

        return True

    def create_test_directories(self):
        """Create necessary test directories."""
        print("Creating test directories...")

        directories = [
            self.script_dir,
            self.script_dir / "reports",
            self.script_dir / "coverage",
            self.script_dir / "logs",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"✓ {directory}")

        return True

    def validate_target_module(self):
        """Validate that the target module exists and can be imported."""
        print("Validating target module (data_anonymizer.py)...")

        target_module = (
            self.project_root
            / "src"
            / "utilities"
            / "privacy"
            / "data_anonymizer.py"
        )

        if not target_module.exists():
            print(f"ERROR: Target module not found: {target_module}")
            return False

        print(f"✓ Target module found: {target_module}")

        # Try to import the module
        try:
            sys.path.insert(0, str(self.project_root))
            import src.tools.privacy.anonymizer.data_anonymizer

            print("✓ Target module can be imported")
            return True
        except ImportError as e:
            print(f"WARNING: Target module import failed: {e}")
            print(
                "This may be expected due to dependency issues in the module"
            )
            return True  # Continue anyway

    def generate_test_script(self):
        """Generate a test execution script."""
        print("Generating test execution script...")

        script_content = f'''#!/usr/bin/env python3
"""
Quick Test Execution Script for Data Anonymizer
Generated: 2025-08-27
"""

import subprocess
import sys
from pathlib import Path

def run_tests():
    """Run the data anonymizer unit tests."""
    test_dir = Path(__file__).parent
    test_file = test_dir / "test_data_anonymizer_2025-08-27.py"
    
    if not test_file.exists():
        print(f"ERROR: Test file not found: {{test_file}}")
        return False
    
    cmd = [
        sys.executable, '-m', 'pytest',
        str(test_file),
        '-v',
        '--html=result_data_anonymizer_report_2025-08-27.html',
        '--self-contained-html',
        '--json-report',
        '--json-report-file=result_data_anonymizer_report_2025-08-27.json',
        '--cov=src.tools.privacy.anonymizer.data_anonymizer',
        '--cov-report=html:result_data_anonymizer_coverage_2025-08-27',
        '--cov-report=json:result_data_anonymizer_coverage_2025-08-27.json'
    ]
    
    try:
        result = subprocess.run(cmd, cwd=test_dir.parent.parent, check=True)
        print("✓ Tests completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Tests failed with return code: {{e.returncode}}")
        return False

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
'''

        script_file = (
            self.script_dir / "run_tests_data_anonymizer_2025-08-27.py"
        )
        with open(script_file, "w", encoding="utf-8") as f:
            f.write(script_content)

        # Make executable on Unix-like systems
        if platform.system() != "Windows":
            os.chmod(script_file, 0o755)

        print(f"✓ Test execution script created: {script_file}")
        return True

    def print_usage_instructions(self):
        """Print usage instructions."""
        print("\n" + "=" * 60)
        print("TEST ENVIRONMENT SETUP COMPLETE")
        print("=" * 60)
        print()
        print("To run the data_anonymizer unit tests:")
        print()
        print("Option 1 - Use the test runner:")
        print(f"  cd {self.script_dir}")
        print("  python test_runner_data_anonymizer_2025-08-27.py")
        print()
        print("Option 2 - Use the quick test script:")
        print(f"  cd {self.script_dir}")
        print("  python run_tests_data_anonymizer_2025-08-27.py")
        print()
        print("Option 3 - Run pytest directly:")
        print(f"  cd {self.project_root}")
        print(
            "  python -m pytest tests/unit/test_data_anonymizer_2025-08-27.py -v"
        )
        print()
        print("Test reports will be generated in:")
        print(
            f"  HTML Report: {self.script_dir}/result_data_anonymizer_report_2025-08-27.html"
        )
        print(
            f"  JSON Report: {self.script_dir}/result_data_anonymizer_report_2025-08-27.json"
        )
        print(
            f"  Coverage: {self.script_dir}/result_data_anonymizer_coverage_2025-08-27/"
        )
        print()

    def run_setup(self):
        """Run the complete setup process."""
        print("Data Anonymizer Test Environment Setup")
        print("=" * 50)
        print()

        steps = [
            ("Checking Python version", self.check_python_version),
            ("Checking pip availability", self.check_pip_availability),
            ("Installing dependencies", self.install_dependencies),
            ("Validating imports", self.validate_imports),
            ("Setting up environment", self.setup_environment_variables),
            ("Creating directories", self.create_test_directories),
            ("Validating target module", self.validate_target_module),
            ("Generating test script", self.generate_test_script),
        ]

        for step_name, step_func in steps:
            print(f"\n{step_name}...")
            if not step_func():
                print(f"FAILED: {step_name}")
                return False

        self.print_usage_instructions()
        return True


def main():
    """Main entry point."""
    setup = TestEnvironmentSetup()
    success = setup.run_setup()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
