#!/usr/bin/env python3
"""
Comprehensive Python Virtual Environment Setup Script
====================================================

This script provides automated setup of Python virtual environments with
cross-platform support, error handling, and comprehensive verification.

Features:
- Automatic requirements.txt cleaning and validation
- Cross-platform virtual environment creation
- Dependency conflict detection and resolution
- Environment isolation verification
- Comprehensive error handling and recovery
- Platform-specific activation scripts

Usage:
    python scripts/setup_venv.py [options]

Options:
    --clean-only        Only clean requirements.txt without setup
    --verify-only       Only verify existing environment
    --force-recreate    Force recreation of existing environment
    --verbose           Enable verbose output
    --python-path       Specify custom Python interpreter path
"""

import os
import sys
import subprocess
import shutil
import json
import re
from pathlib import Path
from typing import Tuple, Optional
import argparse
import logging

# Import our new modules
from venv_manager import VirtualEnvironmentManager
from platform_utils import PlatformUtils
from dependency_resolver import DependencyResolver
from progressive_installer import ProgressiveInstaller


class VirtualEnvironmentSetup:
    """Main class for virtual environment setup and management."""
    
    def __init__(self, project_root: Optional[str] = None,
                 verbose: bool = False):
        """Initialize the setup manager.
        
        Args:
            project_root: Root directory of the project
            verbose: Enable verbose logging
        """
        self.project_root = Path(project_root or os.getcwd())
        self.venv_path = self.project_root / "venv"
        self.requirements_file = self.project_root / "requirements.txt"
        self.requirements_backup = (self.project_root /
                                    "requirements.txt.backup")
        self.setup_log = self.project_root / "venv_setup.log"
        
        # Setup logging
        self.setup_logging(verbose)
        
        # Initialize new utility modules
        self.platform_utils = PlatformUtils(self.logger)
        self.dependency_resolver = DependencyResolver(self.logger)
        self.venv_manager = VirtualEnvironmentManager(
            self.project_root, self.logger)
        
        # Initialize progressive installer (Phase 3)
        self.progressive_installer = ProgressiveInstaller(
            self.venv_manager,
            self.dependency_resolver,
            self.logger
        )
        
        # Platform detection (enhanced)
        self.platform_info = self.platform_utils.get_platform_info()
        self.platform = self.platform_info['system']
        self.is_windows = self.platform_info['is_windows']
        self.is_macos = self.platform_info['is_macos']
        self.is_linux = self.platform_info['is_linux']
        
        # Python executable paths
        self.python_exe = (self.platform_utils.get_recommended_python_path() or
                           self._find_python_executable())
        self.venv_python = self._get_venv_python_path()
        self.venv_pip = self._get_venv_pip_path()
        
        self.logger.info(f"Initialized VirtualEnvironmentSetup for "
                         f"{self.project_root}")
        self.logger.info(f"Platform: {self.platform}")
        self.logger.info(f"Python executable: {self.python_exe}")
        
        # Log platform report
        if verbose:
            platform_report = self.platform_utils.create_platform_report()
            self.logger.debug(f"Platform Report:\n{platform_report}")
    
    def setup_logging(self, verbose: bool = False):
        """Setup logging configuration."""
        log_level = logging.DEBUG if verbose else logging.INFO
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Setup file handler
        file_handler = logging.FileHandler(self.setup_log, mode='w',
                                           encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        
        # Setup console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        
        # Setup logger
        self.logger = logging.getLogger('VenvSetup')
        self.logger.setLevel(log_level)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def _find_python_executable(self) -> str:
        """Find the appropriate Python executable."""
        # Try common Python executable names
        python_names = ['python3', 'python', 'py']
        
        for name in python_names:
            try:
                result = subprocess.run([name, '--version'],
                                        capture_output=True, text=True,
                                        check=True)
                if 'Python 3.' in result.stdout:
                    return name
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        raise RuntimeError("No suitable Python 3 interpreter found")
    
    def _get_venv_python_path(self) -> Path:
        """Get the path to Python executable in virtual environment."""
        if self.is_windows:
            return self.venv_path / "Scripts" / "python.exe"
        else:
            return self.venv_path / "bin" / "python"
    
    def _get_venv_pip_path(self) -> Path:
        """Get the path to pip executable in virtual environment."""
        if self.is_windows:
            return self.venv_path / "Scripts" / "pip.exe"
        else:
            return self.venv_path / "bin" / "pip"
    
    def check_python_version(self) -> Tuple[bool, str]:
        """Check if Python version meets requirements.
        
        Returns:
            Tuple of (is_compatible, version_string)
        """
        try:
            result = subprocess.run([self.python_exe, '--version'],
                                    capture_output=True, text=True,
                                    check=True)
            version_str = result.stdout.strip()
            
            # Extract version numbers
            version_match = re.search(r'Python (\d+)\.(\d+)\.(\d+)',
                                      version_str)
            if not version_match:
                return False, version_str
            
            major, minor, patch = map(int, version_match.groups())
            
            # Check minimum version (Python 3.7+)
            is_compatible = (major == 3 and minor >= 7) or major > 3
            
            self.logger.info(f"Python version: {version_str}")
            self.logger.info(f"Compatible: {is_compatible}")
            
            return is_compatible, version_str
            
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            self.logger.error(f"Failed to check Python version: {e}")
            return False, "Unknown"
    
    def clean_requirements_file(self) -> bool:
        """Clean and validate requirements.txt file.
        
        Returns:
            True if successful, False otherwise
        """
        self.logger.info("Starting requirements.txt cleanup...")
        
        if not self.requirements_file.exists():
            self.logger.error(f"Requirements file not found: "
                              f"{self.requirements_file}")
            return False
        
        try:
            # Create backup
            shutil.copy2(self.requirements_file, self.requirements_backup)
            self.logger.info(f"Created backup: {self.requirements_backup}")
            
            # Read and clean the file
            with open(self.requirements_file, 'r', encoding='utf-8',
                      errors='ignore') as f:
                content = f.read()
            
            # Clean encoding issues (remove extra spaces between characters)
            cleaned_lines = []
            for line in content.splitlines():
                # Remove extra spaces between characters
                cleaned_line = re.sub(r'(\w)\s+(\w)', r'\1\2', line.strip())
                # Remove extra spaces around operators
                cleaned_line = re.sub(r'\s*(==|>=|<=|>|<|!=)\s*', r'\1',
                                      cleaned_line)
                
                if cleaned_line and not cleaned_line.startswith('#'):
                    cleaned_lines.append(cleaned_line)
            
            # Write cleaned content
            with open(self.requirements_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(cleaned_lines) + '\n')
            
            self.logger.info(f"Cleaned {len(cleaned_lines)} package "
                             f"requirements")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to clean requirements file: {e}")
            # Restore backup if cleaning failed
            if self.requirements_backup.exists():
                shutil.copy2(self.requirements_backup, self.requirements_file)
                self.logger.info("Restored original requirements file")
            return False
    
    def create_virtual_environment(self, force_recreate: bool = False) -> bool:
        """Create virtual environment.
        
        Args:
            force_recreate: Force recreation if environment exists
            
        Returns:
            True if successful, False otherwise
        """
        self.logger.info("Creating virtual environment...")
        
        # Check if environment already exists
        if self.venv_path.exists():
            if force_recreate:
                self.logger.info("Removing existing virtual environment...")
                shutil.rmtree(self.venv_path)
            else:
                self.logger.info("Virtual environment already exists")
                return True
        
        try:
            # Create virtual environment
            cmd = [self.python_exe, '-m', 'venv', str(self.venv_path)]
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            self.logger.info("Virtual environment created successfully")
            
            # Upgrade pip in virtual environment
            self.logger.info("Upgrading pip...")
            upgrade_cmd = [str(self.venv_python), '-m', 'pip', 'install',
                           '--upgrade', 'pip']
            subprocess.run(upgrade_cmd, capture_output=True, text=True,
                           check=True)
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to create virtual environment: {e}")
            self.logger.error(f"Command output: {e.stderr}")
            return False
    
    def install_dependencies(self) -> bool:
        """Install dependencies from requirements.txt.
        
        Returns:
            True if successful, False otherwise
        """
        self.logger.info("Installing dependencies...")
        
        if not self.requirements_file.exists():
            self.logger.error("Requirements file not found")
            return False
        
        if not self.venv_python.exists():
            self.logger.error("Virtual environment not found")
            return False
        
        try:
            # Install dependencies
            cmd = [
                str(self.venv_python), '-m', 'pip', 'install', 
                '-r', str(self.requirements_file),
                '--timeout', '300',  # 5 minute timeout
                '--retries', '3'
            ]
            
            self.logger.info(f"Running: {' '.join(cmd)}")
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            self.logger.info("Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install dependencies: {e}")
            self.logger.error(f"Command output: {e.stderr}")
            return False
    
    def verify_environment(self) -> bool:
        """Verify virtual environment setup.
        
        Returns:
            True if verification passes, False otherwise
        """
        self.logger.info("Verifying virtual environment...")
        
        # Check if virtual environment exists
        if not self.venv_path.exists():
            self.logger.error("Virtual environment directory not found")
            return False
        
        # Check Python executable
        if not self.venv_python.exists():
            self.logger.error("Python executable not found in virtual "
                              "environment")
            return False
        
        try:
            # Check Python path isolation
            cmd = [str(self.venv_python), '-c',
                   'import sys; print(sys.executable)']
            result = subprocess.run(cmd, capture_output=True, text=True,
                                    check=True)
            venv_python_path = result.stdout.strip()
            
            if str(self.venv_python) not in venv_python_path:
                self.logger.error(f"Python path not isolated: "
                                  f"{venv_python_path}")
                return False
            
            self.logger.info(f"Python path verified: {venv_python_path}")
            
            # Check pip installation
            pip_cmd = [str(self.venv_python), '-m', 'pip', '--version']
            result = subprocess.run(pip_cmd, capture_output=True, text=True,
                                    check=True)
            self.logger.info(f"Pip version: {result.stdout.strip()}")
            
            # Verify installed packages
            list_cmd = [str(self.venv_python), '-m', 'pip', 'list',
                        '--format=json']
            result = subprocess.run(list_cmd, capture_output=True, text=True,
                                    check=True)
            installed_packages = json.loads(result.stdout)
            
            self.logger.info(f"Installed {len(installed_packages)} packages")
            
            # Test critical imports
            critical_packages = ['PyQt5', 'numpy', 'pandas', 'cryptography']
            for package in critical_packages:
                try:
                    import_cmd = [str(self.venv_python), '-c',
                                  f'import {package.lower()}; '
                                  f'print("{package} OK")']
                    result = subprocess.run(import_cmd, capture_output=True,
                                            text=True, check=True)
                    self.logger.info(f"Import test passed: {package}")
                except subprocess.CalledProcessError:
                    self.logger.warning(f"Import test failed: {package}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Verification failed: {e}")
            return False
    
    def create_activation_scripts(self) -> bool:
        """Create platform-specific activation helper scripts.
        
        Returns:
            True if successful, False otherwise
        """
        self.logger.info("Creating activation scripts...")
        
        scripts_dir = self.project_root / "scripts" / "activation_helpers"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Windows batch script
            batch_script = scripts_dir / "activate.bat"
            with open(batch_script, 'w') as f:
                f.write('@echo off\n')
                f.write(f'call "{self.venv_path}\\Scripts\\activate.bat"\n')
                f.write('echo Virtual environment activated!\n')
                f.write('echo Python: %VIRTUAL_ENV%\\Scripts\\python.exe\n')
                f.write('echo To deactivate, run: deactivate\n')
            
            # Windows PowerShell script
            ps_script = scripts_dir / "activate.ps1"
            with open(ps_script, 'w') as f:
                f.write(f'& "{self.venv_path}\\Scripts\\Activate.ps1"\n')
                f.write('Write-Host "Virtual environment activated!" '
                        '-ForegroundColor Green\n')
                f.write('Write-Host "Python: '
                        '$env:VIRTUAL_ENV\\Scripts\\python.exe" '
                        '-ForegroundColor Cyan\n')
                f.write('Write-Host "To deactivate, run: deactivate" '
                        '-ForegroundColor Yellow\n')
            
            # Unix shell script
            shell_script = scripts_dir / "activate.sh"
            with open(shell_script, 'w') as f:
                f.write('#!/bin/bash\n')
                f.write(f'source "{self.venv_path}/bin/activate"\n')
                f.write('echo "Virtual environment activated!"\n')
                f.write('echo "Python: $VIRTUAL_ENV/bin/python"\n')
                f.write('echo "To deactivate, run: deactivate"\n')
            
            # Fish shell script (new)
            fish_script = scripts_dir / "activate.fish"
            if not fish_script.exists():
                with open(fish_script, 'w') as f:
                    f.write('#!/usr/bin/env fish\n')
                    f.write(f'source "{self.venv_path}/bin/activate.fish"\n')
                    f.write('echo "Virtual environment activated!"\n')
                    f.write('echo "Python: $VIRTUAL_ENV/bin/python"\n')
                    f.write('echo "To deactivate, run: deactivate"\n')
            
            # Make shell scripts executable
            if not self.is_windows:
                os.chmod(shell_script, 0o755)
                os.chmod(fish_script, 0o755)
            
            self.logger.info("Activation scripts created successfully "
                             "(including Fish shell)")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create activation scripts: {e}")
            return False
    
    def run_full_setup(self, force_recreate: bool = False,
                       use_progressive: bool = False) -> bool:
        """Run the complete setup process with enhanced validation.
        
        Args:
            force_recreate: Force recreation of existing environment
            use_progressive: Use progressive installation strategy (Phase 3)
            
        Returns:
            True if successful, False otherwise
        """
        self.logger.info("Starting enhanced virtual environment setup...")
        
        # Enhanced system requirements check
        self.logger.info("Checking system requirements...")
        requirements_check = self.platform_utils.check_system_requirements()
        
        failed_requirements = [req for req, passed in
                               requirements_check.items() if not passed]
        if failed_requirements:
            self.logger.warning(f"System requirements check failed: "
                                f"{failed_requirements}")
            
            # Show platform-specific requirements
            platform_reqs = (self.platform_utils.
                             get_platform_specific_requirements())
            if platform_reqs:
                self.logger.info("Platform-specific requirements:")
                for req in platform_reqs:
                    self.logger.info(f"  - {req}")
        
        # Validate Python installation
        python_validation = self.platform_utils.validate_python_installation()
        issues = python_validation.get('issues', [])
        if isinstance(issues, list) and issues:
            self.logger.warning("Python installation issues detected:")
            for issue in issues:
                self.logger.warning(f"  - {issue}")
        
        # Check Python version
        is_compatible, version = self.check_python_version()
        if not is_compatible:
            self.logger.error(f"Incompatible Python version: {version}")
            return False
        
        # Analyze requirements file for conflicts
        if self.requirements_file.exists():
            self.logger.info("Analyzing requirements for conflicts...")
            analysis = self.dependency_resolver.analyze_requirements_file(
                self.requirements_file)
            
            if analysis.get('conflicts'):
                self.logger.warning(f"Found {len(analysis['conflicts'])} "
                                    f"dependency conflicts")
                for conflict in analysis['conflicts']:
                    if isinstance(conflict, dict):
                        pkg_name = conflict.get('package', 'unknown')
                        severity = conflict.get('severity', 'unknown')
                        self.logger.warning(f"  - {pkg_name}: "
                                            f"{severity} severity")
            
            if analysis.get('suggestions'):
                self.logger.info("Dependency suggestions:")
                for suggestion in analysis['suggestions']:
                    self.logger.info(f"  - {suggestion}")
        
        # Clean requirements file
        if not self.clean_requirements_file():
            self.logger.error("Failed to clean requirements file")
            return False
        
        # Create virtual environment using enhanced manager
        if not self.venv_manager.create_environment(
            python_path=self.python_exe,
            force_recreate=force_recreate,
            upgrade_deps=True
        ):
            self.logger.error("Failed to create virtual environment")
            return False
        
        # Install dependencies with enhanced error handling
        if use_progressive:
            self.logger.info("Using progressive installation strategy (Phase 3)")
            if not self.progressive_installer.install_from_requirements(
                self.requirements_file
            ):
                self.logger.error("Progressive installation failed")
                return False
        else:
            if not self.venv_manager.install_packages(
                requirements_file=self.requirements_file,
                timeout=600
            ):
                self.logger.error("Failed to install dependencies")
                return False
        
        # Create activation scripts (including Fish shell)
        if not self.create_activation_scripts():
            self.logger.error("Failed to create activation scripts")
            return False
        
        # Enhanced environment verification
        if not self.venv_manager.verify_isolation():
            self.logger.error("Environment isolation verification failed")
            return False
        
        if not self.verify_environment():
            self.logger.error("Environment verification failed")
            return False
        
        # Create environment snapshot
        snapshot = self.venv_manager.create_environment_snapshot()
        if snapshot:
            self.logger.info(f"Environment snapshot created: "
                             f"hash {snapshot['environment_hash']}")
        
        # Display environment info
        env_info = self.venv_manager.get_environment_info()
        self.logger.info(f"Environment size: {env_info['size_mb']} MB")
        self.logger.info(f"Installed packages: {env_info['package_count']}")
        
        self.logger.info("Enhanced virtual environment setup completed "
                         "successfully!")
        self.logger.info(f"To activate: source {self.venv_path}/bin/activate "
                         f"(Unix) or {self.venv_path}\\Scripts\\activate.bat "
                         f"(Windows)")
        
        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Comprehensive Python Virtual Environment Setup")
    parser.add_argument('--clean-only', action='store_true',
                        help='Only clean requirements.txt without setup')
    parser.add_argument('--verify-only', action='store_true',
                        help='Only verify existing environment')
    parser.add_argument('--force-recreate', action='store_true',
                        help='Force recreation of existing environment')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose output')
    parser.add_argument('--python-path', type=str,
                        help='Specify custom Python interpreter path')
    parser.add_argument('--progressive', action='store_true',
                        help='Use progressive installation strategy (Phase 3)')
    
    args = parser.parse_args()
    
    try:
        # Initialize setup manager
        setup = VirtualEnvironmentSetup(verbose=args.verbose)
        
        # Override Python path if specified
        if args.python_path:
            setup.python_exe = args.python_path
            setup.logger.info(f"Using custom Python path: {args.python_path}")
        
        success = False
        
        if args.clean_only:
            success = setup.clean_requirements_file()
        elif args.verify_only:
            success = setup.verify_environment()
        else:
            success = setup.run_full_setup(
                args.force_recreate, args.progressive
            )
        
        if success:
            print("\n✅ Operation completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Operation failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()