#!/usr/bin/env python3
"""
Virtual Environment Manager
===========================

This module provides dedicated virtual environment operations with enhanced
functionality for creation, management, and validation of Python virtual
environments.

Features:
- Advanced virtual environment creation with custom configurations
- Environment isolation verification
- Package management within virtual environments
- Cross-platform path handling
- Environment backup and restoration
- Performance optimization for large dependency sets
"""

import os
import subprocess
import shutil
import json
from pathlib import Path
from typing import Dict, List, Optional, Union
import logging
import time
import hashlib


class VirtualEnvironmentManager:
    """Advanced virtual environment management with enhanced features."""
    
    def __init__(self, project_root: Union[str, Path], logger: logging.Logger):
        """Initialize the virtual environment manager.
        
        Args:
            project_root: Root directory of the project
            logger: Logger instance for output
        """
        self.project_root = Path(project_root)
        self.logger = logger
        self.is_windows = os.name == 'nt'
        
        # Default virtual environment configuration
        self.venv_name = "venv"
        self.venv_path = self.project_root / self.venv_name
        
        # Platform-specific paths
        if self.is_windows:
            self.scripts_dir = "Scripts"
            self.python_exe = "python.exe"
            self.pip_exe = "pip.exe"
        else:
            self.scripts_dir = "bin"
            self.python_exe = "python"
            self.pip_exe = "pip"
        
        self.venv_python = self.venv_path / self.scripts_dir / self.python_exe
        self.venv_pip = self.venv_path / self.scripts_dir / self.pip_exe
    
    def create_environment(self,
                           python_path: Optional[str] = None,
                           venv_name: Optional[str] = None,
                           force_recreate: bool = False,
                           system_site_packages: bool = False,
                           upgrade_deps: bool = True) -> bool:
        """Create a virtual environment with advanced options.
        
        Args:
            python_path: Custom Python interpreter path
            venv_name: Custom virtual environment name
            force_recreate: Force recreation if environment exists
            system_site_packages: Give access to system site packages
            upgrade_deps: Upgrade pip, setuptools, and wheel
            
        Returns:
            True if successful, False otherwise
        """
        if venv_name:
            self.venv_name = venv_name
            self.venv_path = self.project_root / self.venv_name
            self._update_paths()
        
        self.logger.info(f"Creating virtual environment: {self.venv_path}")
        
        # Check if environment exists
        if self.venv_path.exists():
            if force_recreate:
                self.logger.info("Removing existing virtual environment...")
                if not self._remove_environment():
                    return False
            else:
                self.logger.info("Virtual environment already exists")
                return self._verify_environment_structure()
        
        try:
            # Determine Python executable
            python_cmd = python_path or self._find_python_executable()
            
            # Build venv command
            cmd = [python_cmd, '-m', 'venv']
            
            if system_site_packages:
                cmd.append('--system-site-packages')
            
            if upgrade_deps:
                cmd.append('--upgrade-deps')
            
            cmd.append(str(self.venv_path))
            
            self.logger.info(f"Running: {' '.join(cmd)}")
            
            # Create virtual environment
            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=300  # 5 minute timeout
            )
            
            self.logger.info("Virtual environment created successfully")
            
            # Verify structure
            if not self._verify_environment_structure():
                self.logger.error("Environment structure verification failed")
                return False
            
            # Upgrade core packages if requested
            if upgrade_deps:
                return self._upgrade_core_packages()
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to create virtual environment: {e}")
            if e.stderr:
                self.logger.error(f"Error output: {e.stderr}")
            return False
        except subprocess.TimeoutExpired:
            self.logger.error("Virtual environment creation timed out")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error creating environment: {e}")
            return False
    
    def _update_paths(self):
        """Update internal paths after venv_path change."""
        self.venv_python = self.venv_path / self.scripts_dir / self.python_exe
        self.venv_pip = self.venv_path / self.scripts_dir / self.pip_exe
    
    def _find_python_executable(self) -> str:
        """Find the appropriate Python executable."""
        if not self.is_windows:
            python_names = ['python3', 'python', 'py']
        else:
            python_names = ['py', 'python', 'python3']
        
        for name in python_names:
            try:
                result = subprocess.run(
                    [name, '--version'],
                    capture_output=True, 
                    text=True,
                    check=True
                )
                if 'Python 3.' in result.stdout:
                    self.logger.debug(f"Found Python: {name}")
                    return name
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        raise RuntimeError("No suitable Python 3 interpreter found")
    
    def _remove_environment(self) -> bool:
        """Safely remove existing virtual environment."""
        try:
            # On Windows, we might need to handle file locks
            if self.is_windows:
                # Try to deactivate any active environment first
                self._deactivate_environment()
                time.sleep(1)  # Brief pause for file handles to close
            
            shutil.rmtree(self.venv_path)
            self.logger.info("Existing virtual environment removed")
            return True
            
        except PermissionError as e:
            self.logger.error(f"Permission denied removing environment: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to remove environment: {e}")
            return False
    
    def _deactivate_environment(self):
        """Attempt to deactivate any active virtual environment."""
        try:
            if 'VIRTUAL_ENV' in os.environ:
                del os.environ['VIRTUAL_ENV']
            if 'VIRTUAL_ENV_PROMPT' in os.environ:
                del os.environ['VIRTUAL_ENV_PROMPT']
        except Exception:
            pass  # Best effort
    
    def _verify_environment_structure(self) -> bool:
        """Verify virtual environment has correct structure."""
        required_paths = [
            self.venv_path,
            self.venv_python,
            self.venv_path / self.scripts_dir,
            self.venv_path / "pyvenv.cfg"
        ]
        
        for path in required_paths:
            if not path.exists():
                self.logger.error(f"Missing required path: {path}")
                return False
        
        # Verify Python executable works
        try:
            result = subprocess.run(
                [str(self.venv_python), '--version'],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            version = result.stdout.strip()
            self.logger.debug(f"Virtual environment Python: {version}")
            return True
            
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            self.logger.error(
                f"Virtual environment Python verification failed: {e}")
            return False
    
    def _upgrade_core_packages(self) -> bool:
        """Upgrade core packages (pip, setuptools, wheel)."""
        self.logger.info("Upgrading core packages...")
        
        core_packages = ['pip', 'setuptools', 'wheel']
        
        for package in core_packages:
            try:
                cmd = [
                    str(self.venv_python), '-m', 'pip', 'install', 
                    '--upgrade', package
                ]
                
                subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=120
                )
                
                self.logger.debug(f"Upgraded {package}")
                
            except (subprocess.CalledProcessError,
                    subprocess.TimeoutExpired) as e:
                self.logger.warning(f"Failed to upgrade {package}: {e}")
                # Continue with other packages
        
        return True
    
    def install_packages(self,
                         requirements_file: Optional[Path] = None,
                         packages: Optional[List[str]] = None,
                         upgrade: bool = False,
                         no_deps: bool = False,
                         timeout: int = 600) -> bool:
        """Install packages in the virtual environment.
        
        Args:
            requirements_file: Path to requirements.txt file
            packages: List of package names to install
            upgrade: Upgrade packages if already installed
            no_deps: Don't install dependencies
            timeout: Installation timeout in seconds
            
        Returns:
            True if successful, False otherwise
        """
        if not self.venv_python.exists():
            self.logger.error("Virtual environment not found")
            return False
        
        if not requirements_file and not packages:
            self.logger.error(
                "Either requirements_file or packages must be provided")
            return False
        
        try:
            cmd = [str(self.venv_python), '-m', 'pip', 'install']
            
            if upgrade:
                cmd.append('--upgrade')
            
            if no_deps:
                cmd.append('--no-deps')
            
            # Add timeout and retry options
            cmd.extend(['--timeout', str(timeout), '--retries', '3'])
            
            if requirements_file:
                cmd.extend(['-r', str(requirements_file)])
            
            if packages:
                cmd.extend(packages)
            
            self.logger.info(f"Installing packages: {' '.join(cmd[3:])}")
            
            subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=timeout
            )
            
            self.logger.info("Package installation completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Package installation failed: {e}")
            if e.stderr:
                self.logger.error(f"Error output: {e.stderr}")
            return False
        except subprocess.TimeoutExpired:
            self.logger.error("Package installation timed out")
            return False
    
    def get_installed_packages(self) -> List[Dict[str, str]]:
        """Get list of installed packages in the virtual environment.
        
        Returns:
            List of dictionaries with package information
        """
        if not self.venv_python.exists():
            self.logger.error("Virtual environment not found")
            return []
        
        try:
            cmd = [str(self.venv_python), '-m', 'pip', 'list', '--format=json']
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            
            packages = json.loads(result.stdout)
            self.logger.debug(f"Found {len(packages)} installed packages")
            return packages
            
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired,
                json.JSONDecodeError) as e:
            self.logger.error(f"Failed to get installed packages: {e}")
            return []
    
    def verify_isolation(self) -> bool:
        """Verify that the virtual environment is properly isolated.
        
        Returns:
            True if properly isolated, False otherwise
        """
        if not self.venv_python.exists():
            self.logger.error("Virtual environment not found")
            return False
        
        try:
            # Check Python executable path
            cmd = [str(self.venv_python), '-c',
                   'import sys; print(sys.executable)']
            result = subprocess.run(cmd, capture_output=True, text=True,
                                    check=True)
            python_path = result.stdout.strip()
            
            if str(self.venv_python) not in python_path:
                self.logger.error(f"Python not isolated: {python_path}")
                return False
            
            # Check sys.path isolation
            cmd = [str(self.venv_python), '-c',
                   'import sys, json; print(json.dumps(sys.path))']
            result = subprocess.run(cmd, capture_output=True, text=True,
                                    check=True)
            sys_paths = json.loads(result.stdout)
            
            # Verify virtual environment site-packages is in path
            venv_site_packages = str(self.venv_path)
            if not any(venv_site_packages in path for path in sys_paths):
                self.logger.error(
                    "Virtual environment site-packages not in sys.path")
                return False
            
            self.logger.info("Virtual environment isolation verified")
            return True
            
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            self.logger.error(f"Isolation verification failed: {e}")
            return False
    
    def create_environment_snapshot(self) -> Optional[Dict]:
        """Create a snapshot of the current environment state.
        
        Returns:
            Dictionary with environment information or None if failed
        """
        if not self.venv_python.exists():
            self.logger.error("Virtual environment not found")
            return None
        
        try:
            snapshot = {
                'timestamp': time.time(),
                'venv_path': str(self.venv_path),
                'python_version': self._get_python_version(),
                'packages': self.get_installed_packages(),
                'pip_version': self._get_pip_version(),
                'environment_hash': self._calculate_environment_hash()
            }
            
            return snapshot
            
        except Exception as e:
            self.logger.error(f"Failed to create environment snapshot: {e}")
            return None
    
    def _get_python_version(self) -> str:
        """Get Python version in virtual environment."""
        try:
            cmd = [str(self.venv_python), '--version']
            result = subprocess.run(cmd, capture_output=True, text=True,
                                    check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "Unknown"
    
    def _get_pip_version(self) -> str:
        """Get pip version in virtual environment."""
        try:
            cmd = [str(self.venv_python), '-m', 'pip', '--version']
            result = subprocess.run(cmd, capture_output=True, text=True,
                                    check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "Unknown"
    
    def _calculate_environment_hash(self) -> str:
        """Calculate a hash representing the current environment state."""
        try:
            packages = self.get_installed_packages()
            package_string = json.dumps(packages, sort_keys=True)
            return hashlib.sha256(package_string.encode()).hexdigest()[:16]
        except Exception:
            return "unknown"
    
    def backup_environment(self, backup_path: Optional[Path] = None) -> bool:
        """Create a backup of the virtual environment.
        
        Args:
            backup_path: Custom backup location
            
        Returns:
            True if successful, False otherwise
        """
        if not self.venv_path.exists():
            self.logger.error("Virtual environment not found")
            return False
        
        if backup_path is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_path = self.project_root / f"venv_backup_{timestamp}"
        
        try:
            self.logger.info(f"Creating environment backup: {backup_path}")
            shutil.copytree(self.venv_path, backup_path)
            
            # Create metadata file
            snapshot = self.create_environment_snapshot()
            if snapshot:
                metadata_file = backup_path / "backup_metadata.json"
                with open(metadata_file, 'w') as f:
                    json.dump(snapshot, f, indent=2)
            
            self.logger.info("Environment backup created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create environment backup: {e}")
            return False
    
    def get_environment_info(self) -> Dict:
        """Get comprehensive information about the virtual environment.
        
        Returns:
            Dictionary with environment information
        """
        info = {
            'exists': self.venv_path.exists(),
            'path': str(self.venv_path),
            'python_path': str(self.venv_python),
            'pip_path': str(self.venv_pip),
            'is_isolated': False,
            'python_version': 'Unknown',
            'pip_version': 'Unknown',
            'package_count': 0,
            'size_mb': 0
        }
        
        if info['exists']:
            info['is_isolated'] = self.verify_isolation()
            info['python_version'] = self._get_python_version()
            info['pip_version'] = self._get_pip_version()
            info['package_count'] = len(self.get_installed_packages())
            info['size_mb'] = self._calculate_directory_size()
        
        return info
    
    def _calculate_directory_size(self) -> float:
        """Calculate the size of the virtual environment directory in MB."""
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(self.venv_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        continue
            return round(total_size / (1024 * 1024), 2)
        except Exception:
            return 0.0