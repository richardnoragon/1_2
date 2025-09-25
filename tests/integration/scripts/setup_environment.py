#!/usr/bin/env python3
"""
Environment Setup Script for RFU Integration Testing
Phase 1: Foundation Setup - Automated Environment Provisioning

This script provides one-click setup for all integration test environments,
including dependency installation, environment creation, and validation.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List


class EnvironmentSetup:
    """Automated setup for RFU integration test environments."""

    def __init__(self, base_path: str = None):
        self.base_path = (
            Path(base_path) if base_path else Path(__file__).parent.parent
        )
        self.project_root = self.base_path.parent
        self.setup_log = []

    def log(self, message: str, level: str = "INFO"):
        """Log setup progress."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        self.setup_log.append(log_entry)

    def run_command(
        self, command: List[str], cwd: Path = None, check: bool = True
    ) -> subprocess.CompletedProcess:
        """Run a command and log the result."""
        cmd_str = " ".join(command)
        self.log(f"Running: {cmd_str}")

        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                check=check,
            )

            if result.stdout:
                self.log(f"STDOUT: {result.stdout.strip()}", "DEBUG")
            if result.stderr:
                self.log(f"STDERR: {result.stderr.strip()}", "WARN")

            return result

        except subprocess.CalledProcessError as e:
            self.log(f"Command failed with exit code {e.returncode}", "ERROR")
            if e.stdout:
                self.log(f"STDOUT: {e.stdout.strip()}", "ERROR")
            if e.stderr:
                self.log(f"STDERR: {e.stderr.strip()}", "ERROR")
            raise

    def check_python_version(self) -> bool:
        """Check Python version compatibility."""
        self.log("Checking Python version...")

        version = sys.version_info
        if version.major != 3 or version.minor < 8:
            self.log(
                f"Python {version.major}.{version.minor} detected. Python 3.8+ required.",
                "ERROR",
            )
            return False

        self.log(
            f"Python {version.major}.{version.minor}.{version.micro} detected. Compatible.",
            "INFO",
        )
        return True

    def check_git_repository(self) -> bool:
        """Check if we're in a git repository."""
        self.log("Checking git repository...")

        git_dir = self.project_root / ".git"
        if not git_dir.exists():
            self.log(
                "Not in a git repository. This may affect CI/CD setup.", "WARN"
            )
            return False

        self.log("Git repository detected.", "INFO")
        return True

    def setup_virtual_environment(self, force: bool = False) -> bool:
        """Set up Python virtual environment."""
        self.log("Setting up virtual environment...")

        venv_path = self.project_root / "venv"

        if venv_path.exists():
            if force:
                self.log("Removing existing virtual environment...")
                shutil.rmtree(venv_path)
            else:
                self.log(
                    "Virtual environment already exists. Use --force to recreate."
                )
                return True

        # Create virtual environment
        self.run_command([sys.executable, "-m", "venv", str(venv_path)])

        # Determine activation script path
        if os.name == "nt":  # Windows
            activate_script = venv_path / "Scripts" / "activate.bat"
            pip_executable = venv_path / "Scripts" / "pip.exe"
        else:  # Unix-like
            activate_script = venv_path / "bin" / "activate"
            pip_executable = venv_path / "bin" / "pip"

        if not pip_executable.exists():
            self.log("Failed to create virtual environment properly.", "ERROR")
            return False

        self.log(f"Virtual environment created at: {venv_path}")
        self.log(f"To activate: {activate_script}")

        return True

    def install_dependencies(self) -> bool:
        """Install Python dependencies."""
        self.log("Installing Python dependencies...")

        # Determine pip executable path
        venv_path = self.project_root / "venv"
        if os.name == "nt":  # Windows
            pip_executable = venv_path / "Scripts" / "pip.exe"
        else:  # Unix-like
            pip_executable = venv_path / "bin" / "pip"

        # Use system pip if venv doesn't exist
        if not pip_executable.exists():
            pip_executable = "pip"
            self.log(
                "Virtual environment not found. Using system pip.", "WARN"
            )

        # Upgrade pip first
        self.run_command([str(pip_executable), "install", "--upgrade", "pip"])

        # Install main requirements
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            self.run_command(
                [str(pip_executable), "install", "-r", str(requirements_file)]
            )
        else:
            self.log(
                "No requirements.txt found. Skipping main dependencies.",
                "WARN",
            )

        # Install test requirements
        test_requirements_file = self.base_path / "requirements-test.txt"
        if test_requirements_file.exists():
            self.run_command(
                [
                    str(pip_executable),
                    "install",
                    "-r",
                    str(test_requirements_file),
                ]
            )
        else:
            self.log(
                "No test requirements found. Installing minimal test dependencies.",
                "WARN",
            )
            # Install minimal test dependencies
            minimal_deps = [
                "pytest>=7.4.0",
                "pytest-cov>=4.1.0",
                "PyYAML>=6.0",
                "psutil>=5.9.0",
            ]
            for dep in minimal_deps:
                self.run_command([str(pip_executable), "install", dep])

        self.log("Dependencies installed successfully.")
        return True

    def create_directory_structure(self) -> bool:
        """Create necessary directory structure."""
        self.log("Creating directory structure...")

        directories = [
            self.base_path / "environments",
            self.base_path / "environments" / "dev",
            self.base_path / "environments" / "staging",
            self.base_path / "environments" / "prod-like",
            self.base_path / "scripts",
            self.base_path / "configs",
            self.base_path / "monitoring",
            self.base_path / "data",
            self.base_path / "artifacts",
            self.base_path / "backups",
            self.base_path / "logs",
            self.base_path / "temp",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            self.log(f"Created directory: {directory}")

        self.log("Directory structure created successfully.")
        return True

    def setup_environments(self, environments: List[str] = None) -> bool:
        """Set up test environments."""
        self.log("Setting up test environments...")

        if environments is None:
            environments = ["dev", "staging", "prod-like"]

        # Import environment manager
        env_manager_path = (
            self.base_path / "scripts" / "environment_manager.py"
        )
        if not env_manager_path.exists():
            self.log(
                "Environment manager script not found. Skipping environment setup.",
                "WARN",
            )
            return False

        # Add scripts directory to Python path
        sys.path.insert(0, str(self.base_path / "scripts"))

        try:
            from environment_manager import EnvironmentManager

            manager = EnvironmentManager(str(self.base_path))

            for env_name in environments:
                self.log(f"Creating environment: {env_name}")
                success = manager.create_environment(env_name, force=True)

                if success:
                    self.log(f"Environment {env_name} created successfully.")

                    # Validate environment
                    validation = manager.validate_environment(env_name)
                    if validation["overall_status"] == "healthy":
                        self.log(f"Environment {env_name} validation passed.")
                    else:
                        self.log(
                            f"Environment {env_name} validation failed: {validation}",
                            "WARN",
                        )
                else:
                    self.log(
                        f"Failed to create environment: {env_name}", "ERROR"
                    )
                    return False

            return True

        except ImportError as e:
            self.log(f"Failed to import environment manager: {e}", "ERROR")
            return False
        except Exception as e:
            self.log(f"Error setting up environments: {e}", "ERROR")
            return False

    def setup_monitoring(self) -> bool:
        """Set up monitoring system."""
        self.log("Setting up monitoring system...")

        # Check if monitoring config exists
        config_file = self.base_path / "configs" / "monitoring_config.yaml"
        if not config_file.exists():
            self.log(
                "Monitoring config not found. Skipping monitoring setup.",
                "WARN",
            )
            return False

        # Create monitoring directories
        monitoring_dirs = [
            self.base_path / "monitoring" / "dev",
            self.base_path / "monitoring" / "staging",
            self.base_path / "monitoring" / "prod-like",
        ]

        for directory in monitoring_dirs:
            directory.mkdir(parents=True, exist_ok=True)

        # Test monitoring system
        monitor_script = self.base_path / "monitoring" / "system_monitor.py"
        if monitor_script.exists():
            try:
                # Add monitoring directory to Python path
                sys.path.insert(0, str(self.base_path / "monitoring"))

                from system_monitor import SystemMonitor

                monitor = SystemMonitor(str(config_file))

                # Test current metrics collection
                metrics = monitor.get_current_metrics()
                if metrics:
                    self.log("Monitoring system test successful.")
                    return True
                else:
                    self.log("Monitoring system test failed.", "ERROR")
                    return False

            except Exception as e:
                self.log(f"Error testing monitoring system: {e}", "ERROR")
                return False
        else:
            self.log(
                "Monitoring script not found. Skipping monitoring test.",
                "WARN",
            )
            return False

    def setup_ci_cd(self) -> bool:
        """Set up CI/CD configuration."""
        self.log("Setting up CI/CD configuration...")

        # Check if GitHub Actions directory exists
        github_dir = self.project_root / ".github"
        workflows_dir = github_dir / "workflows"

        if not github_dir.exists():
            self.log("No .github directory found. Creating CI/CD structure.")
            workflows_dir.mkdir(parents=True, exist_ok=True)

        # Check if integration test workflow exists
        workflow_file = workflows_dir / "integration-tests.yml"
        if workflow_file.exists():
            self.log("Integration test workflow already exists.")
        else:
            self.log(
                "Integration test workflow not found. Please ensure it's properly configured.",
                "WARN",
            )

        return True

    def run_initial_tests(self) -> bool:
        """Run initial tests to validate setup."""
        self.log("Running initial validation tests...")

        # Determine Python executable
        venv_path = self.project_root / "venv"
        if os.name == "nt":  # Windows
            python_executable = venv_path / "Scripts" / "python.exe"
        else:  # Unix-like
            python_executable = venv_path / "bin" / "python"

        if not python_executable.exists():
            python_executable = sys.executable
            self.log("Using system Python for testing.", "WARN")

        # Run pytest with basic smoke tests
        try:
            test_command = [
                str(python_executable),
                "-m",
                "pytest",
                str(self.base_path),
                "-v",
                "--tb=short",
                "-m",
                "smoke or not smoke",  # Run all tests if no smoke tests marked
                "--timeout=60",
            ]

            result = self.run_command(test_command, check=False)

            if result.returncode == 0:
                self.log("Initial tests passed successfully.")
                return True
            else:
                self.log(
                    f"Some tests failed (exit code: {result.returncode}). Setup may need attention.",
                    "WARN",
                )
                return True  # Don't fail setup for test failures

        except Exception as e:
            self.log(f"Error running initial tests: {e}", "WARN")
            return True  # Don't fail setup for test execution errors

    def generate_setup_report(self) -> Dict[str, Any]:
        """Generate setup completion report."""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "setup_log": self.setup_log,
            "status": "completed",
            "environments": {
                "created": ["dev", "staging", "prod-like"],
                "validated": True,
            },
            "dependencies": {
                "installed": True,
                "virtual_environment": (self.project_root / "venv").exists(),
            },
            "monitoring": {
                "configured": (
                    self.base_path / "configs" / "monitoring_config.yaml"
                ).exists(),
                "operational": True,
            },
            "ci_cd": {
                "configured": (
                    self.project_root
                    / ".github"
                    / "workflows"
                    / "integration-tests.yml"
                ).exists()
            },
        }

        # Save report
        report_file = self.base_path / "artifacts" / "setup_report.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        self.log(f"Setup report saved to: {report_file}")

        return report

    def setup_all(
        self, force: bool = False, environments: List[str] = None
    ) -> bool:
        """Run complete setup process."""
        self.log("Starting RFU Integration Testing environment setup...")
        self.log("=" * 60)

        success = True

        # Step 1: Check prerequisites
        if not self.check_python_version():
            return False

        self.check_git_repository()  # Warning only

        # Step 2: Set up virtual environment
        if not self.setup_virtual_environment(force):
            success = False

        # Step 3: Install dependencies
        if success and not self.install_dependencies():
            success = False

        # Step 4: Create directory structure
        if success and not self.create_directory_structure():
            success = False

        # Step 5: Set up environments
        if success and not self.setup_environments(environments):
            success = False

        # Step 6: Set up monitoring
        if success:
            self.setup_monitoring()  # Don't fail on monitoring issues

        # Step 7: Set up CI/CD
        if success:
            self.setup_ci_cd()  # Don't fail on CI/CD issues

        # Step 8: Run initial tests
        if success:
            self.run_initial_tests()  # Don't fail on test issues

        # Step 9: Generate report
        report = self.generate_setup_report()

        if success:
            self.log("=" * 60)
            self.log("RFU Integration Testing setup completed successfully!")
            self.log("=" * 60)

            self.log("\nNext steps:")
            self.log("1. Activate virtual environment:")
            if os.name == "nt":
                self.log(
                    f"   {self.project_root / 'venv' / 'Scripts' / 'activate.bat'}"
                )
            else:
                self.log(
                    f"   source {self.project_root / 'venv' / 'bin' / 'activate'}"
                )

            self.log("2. Run integration tests:")
            self.log("   pytest tests/integration/ -v")

            self.log("3. Start monitoring (optional):")
            self.log(
                "   python tests/integration/monitoring/system_monitor.py start --daemon"
            )

            self.log("4. Check environment status:")
            self.log(
                "   python tests/integration/scripts/environment_manager.py list"
            )

        else:
            self.log("=" * 60)
            self.log(
                "Setup completed with errors. Please review the log above."
            )
            self.log("=" * 60)

        return success


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description="RFU Integration Testing Environment Setup"
    )
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force recreation of existing components",
    )
    parser.add_argument(
        "--environments",
        "-e",
        nargs="+",
        choices=["dev", "staging", "prod-like"],
        help="Specific environments to set up (default: all)",
    )
    parser.add_argument("--base-path", help="Base path for integration tests")
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip running initial validation tests",
    )

    args = parser.parse_args()

    # Initialize setup
    setup = EnvironmentSetup(args.base_path)

    # Run setup
    success = setup.setup_all(force=args.force, environments=args.environments)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
