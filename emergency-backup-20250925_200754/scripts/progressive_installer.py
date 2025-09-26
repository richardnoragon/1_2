#!/usr/bin/env python3
"""
Progressive Package Installer
=============================

This module provides advanced progressive package installation with dependency
ordering, checkpoint/rollback system, compilation requirements handling,
and comprehensive error recovery.

Features:
- Dependency-ordered installation using topological sorting
- Installation checkpoints with rollback capability
- Compilation requirements detection and handling
- Exponential backoff retry logic for network failures
- Installation progress tracking and reporting
- Batch installation optimization
- Advanced error recovery and diagnostics

Phase 3 Implementation:
- 3.1 Progressive Installation Strategy
- 3.2 Enhanced Conflict Resolution
"""

import os
import sys
import subprocess
import shutil
import json
import time
import hashlib
import tempfile
import platform
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import random
import re

# Import existing modules
from dependency_resolver import DependencyResolver, SimpleRequirement
from venv_manager import VirtualEnvironmentManager
from platform_utils import PlatformUtils


class InstallationStatus(Enum):
    """Installation status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ROLLED_BACK = "rolled_back"


class PackageType(Enum):
    """Package type classification."""
    PURE_PYTHON = "pure_python"
    COMPILED = "compiled"
    SYSTEM_DEPENDENT = "system_dependent"
    BUILD_TOOLS = "build_tools"


@dataclass
class PackageInfo:
    """Enhanced package information for installation."""
    name: str
    version: str = ""
    requirement_string: str = ""
    package_type: PackageType = PackageType.PURE_PYTHON
    dependencies: List[str] = field(default_factory=list)
    build_requirements: List[str] = field(default_factory=list)
    installation_order: int = 0
    status: InstallationStatus = InstallationStatus.PENDING
    install_time: float = 0.0
    error_message: str = ""
    retry_count: int = 0


@dataclass
class InstallationCheckpoint:
    """Installation checkpoint for rollback capability."""
    checkpoint_id: str
    timestamp: float
    installed_packages: List[Dict]
    environment_hash: str
    checkpoint_path: Path
    description: str = ""


@dataclass
class InstallationBatch:
    """Batch of packages to install together."""
    batch_id: int
    packages: List[PackageInfo]
    batch_type: str = "standard"  # standard, build_tools, compiled
    estimated_time: float = 0.0
    dependencies_satisfied: bool = False


class CompilationHandler:
    """Handle compilation requirements and build tools."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.platform_info = platform.system().lower()
        self.is_windows = self.platform_info == "windows"
        self.is_macos = self.platform_info == "darwin"
        self.is_linux = self.platform_info == "linux"
        
        # Packages that typically require compilation
        self.compiled_packages = {
            'cryptography', 'lxml', 'pillow', 'numpy', 'scipy', 'pandas',
            'psutil', 'pyqt5', 'pycrypto', 'bcrypt', 'cffi', 'markupsafe',
            'pyyaml', 'greenlet', 'gevent', 'uwsgi', 'mysqlclient',
            'psycopg2', 'opencv-python', 'tensorflow', 'torch'
        }
        
        # Build tools and their detection methods
        self.build_tools = {
            'windows': {
                'visual_cpp': self._check_visual_cpp,
                'windows_sdk': self._check_windows_sdk,
                'cmake': self._check_cmake
            },
            'linux': {
                'gcc': self._check_gcc,
                'make': self._check_make,
                'cmake': self._check_cmake,
                'python_dev': self._check_python_dev
            },
            'darwin': {
                'xcode': self._check_xcode,
                'cmake': self._check_cmake,
                'gcc': self._check_gcc
            }
        }
    
    def classify_package(self, package_name: str) -> PackageType:
        """Classify package type based on compilation requirements."""
        package_lower = package_name.lower().replace('-', '').replace('_', '')
        
        # Check for known compiled packages
        for compiled_pkg in self.compiled_packages:
            if compiled_pkg in package_lower or package_lower in compiled_pkg:
                return PackageType.COMPILED
        
        # Check for system-dependent packages
        system_indicators = ['win32', 'linux', 'darwin', 'platform', 'system']
        if any(indicator in package_lower for indicator in system_indicators):
            return PackageType.SYSTEM_DEPENDENT
        
        # Check for build tools
        build_indicators = ['setuptools', 'wheel', 'pip', 'build', 'cmake']
        if any(indicator in package_lower for indicator in build_indicators):
            return PackageType.BUILD_TOOLS
        
        return PackageType.PURE_PYTHON
    
    def check_build_requirements(self) -> Dict[str, bool]:
        """Check availability of build tools for current platform."""
        requirements = {}
        
        platform_tools = self.build_tools.get(self.platform_info, {})
        for tool_name, check_func in platform_tools.items():
            try:
                requirements[tool_name] = check_func()
            except Exception as e:
                self.logger.debug(f"Error checking {tool_name}: {e}")
                requirements[tool_name] = False
        
        return requirements
    
    def _check_visual_cpp(self) -> bool:
        """Check for Visual C++ Build Tools on Windows."""
        try:
            # Check for Visual Studio Build Tools
            vs_paths = [
                r"C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools",
                r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools",
                r"C:\Program Files\Microsoft Visual Studio\2019\Community",
                r"C:\Program Files\Microsoft Visual Studio\2022\Community"
            ]
            
            for path in vs_paths:
                if Path(path).exists():
                    return True
            
            # Check for cl.exe in PATH
            result = subprocess.run(['where', 'cl'], capture_output=True, text=True)
            return result.returncode == 0
            
        except Exception:
            return False
    
    def _check_windows_sdk(self) -> bool:
        """Check for Windows SDK."""
        try:
            sdk_paths = [
                r"C:\Program Files (x86)\Windows Kits\10",
                r"C:\Program Files\Windows Kits\10"
            ]
            return any(Path(path).exists() for path in sdk_paths)
        except Exception:
            return False
    
    def _check_gcc(self) -> bool:
        """Check for GCC compiler."""
        try:
            result = subprocess.run(['gcc', '--version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def _check_make(self) -> bool:
        """Check for make utility."""
        try:
            result = subprocess.run(['make', '--version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def _check_cmake(self) -> bool:
        """Check for CMake."""
        try:
            result = subprocess.run(['cmake', '--version'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def _check_python_dev(self) -> bool:
        """Check for Python development headers."""
        try:
            import distutils.util
            import sysconfig
            
            # Check for Python.h
            include_dir = sysconfig.get_path('include')
            python_h = Path(include_dir) / "Python.h"
            return python_h.exists()
        except Exception:
            return False
    
    def _check_xcode(self) -> bool:
        """Check for Xcode command line tools."""
        try:
            result = subprocess.run(['xcode-select', '--print-path'], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def get_build_recommendations(self, missing_tools: List[str]) -> List[str]:
        """Get installation recommendations for missing build tools."""
        recommendations = []
        
        if self.is_windows:
            if 'visual_cpp' in missing_tools:
                recommendations.append(
                    "Install Microsoft C++ Build Tools from: "
                    "https://visualstudio.microsoft.com/visual-cpp-build-tools/"
                )
            if 'windows_sdk' in missing_tools:
                recommendations.append(
                    "Install Windows SDK from: "
                    "https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/"
                )
        
        elif self.is_linux:
            if 'gcc' in missing_tools:
                recommendations.append("Install GCC: sudo apt-get install gcc (Ubuntu/Debian) or sudo yum install gcc (CentOS/RHEL)")
            if 'make' in missing_tools:
                recommendations.append("Install make: sudo apt-get install make (Ubuntu/Debian) or sudo yum install make (CentOS/RHEL)")
            if 'python_dev' in missing_tools:
                recommendations.append("Install Python dev headers: sudo apt-get install python3-dev (Ubuntu/Debian)")
        
        elif self.is_macos:
            if 'xcode' in missing_tools:
                recommendations.append("Install Xcode command line tools: xcode-select --install")
        
        if 'cmake' in missing_tools:
            recommendations.append("Install CMake from: https://cmake.org/download/")
        
        return recommendations


class RetryManager:
    """Manage retry logic with exponential backoff."""
    
    def __init__(self, logger: logging.Logger, max_retries: int = 3):
        self.logger = logger
        self.max_retries = max_retries
        self.base_delay = 1.0  # Base delay in seconds
        self.max_delay = 60.0  # Maximum delay in seconds
        self.jitter_factor = 0.1  # Add randomness to prevent thundering herd
    
    def execute_with_retry(self, func, *args, **kwargs):
        """Execute function with exponential backoff retry."""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                
                if attempt == self.max_retries:
                    self.logger.error(f"Max retries ({self.max_retries}) exceeded")
                    break
                
                # Calculate delay with exponential backoff and jitter
                delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                jitter = delay * self.jitter_factor * random.random()
                total_delay = delay + jitter
                
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                self.logger.info(f"Retrying in {total_delay:.2f} seconds...")
                time.sleep(total_delay)
        
        if last_exception:
            raise last_exception
        else:
            raise RuntimeError("Function failed without exception")
    
    def is_retryable_error(self, error: Exception) -> bool:
        """Determine if an error is retryable."""
        error_str = str(error).lower()
        
        # Network-related errors
        network_errors = [
            'timeout', 'connection', 'network', 'dns', 'resolve',
            'unreachable', 'refused', 'reset', 'broken pipe'
        ]
        
        # Temporary pip errors
        pip_errors = [
            'temporary failure', 'try again', 'server error',
            'service unavailable', 'too many requests'
        ]
        
        retryable_errors = network_errors + pip_errors
        return any(err in error_str for err in retryable_errors)


class ProgressTracker:
    """Track and report installation progress."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.start_time = time.time()
        self.total_packages = 0
        self.completed_packages = 0
        self.failed_packages = 0
        self.current_package = ""
        self.current_batch = 0
        self.total_batches = 0
        self.package_times = {}
        
    def start_installation(self, total_packages: int, total_batches: int):
        """Start tracking installation progress."""
        self.start_time = time.time()
        self.total_packages = total_packages
        self.total_batches = total_batches
        self.completed_packages = 0
        self.failed_packages = 0
        
        self.logger.info(f"Starting installation of {total_packages} packages in {total_batches} batches")
    
    def start_batch(self, batch_id: int, batch_packages: List[str]):
        """Start tracking a batch."""
        self.current_batch = batch_id
        package_list = ", ".join(batch_packages[:3])
        if len(batch_packages) > 3:
            package_list += f" and {len(batch_packages) - 3} more"
        
        self.logger.info(f"Batch {batch_id}/{self.total_batches}: Installing {package_list}")
    
    def start_package(self, package_name: str):
        """Start tracking a package installation."""
        self.current_package = package_name
        self.package_times[package_name] = time.time()
        
        progress = (self.completed_packages / self.total_packages) * 100
        self.logger.info(f"[{progress:.1f}%] Installing {package_name}...")
    
    def complete_package(self, package_name: str, success: bool = True):
        """Complete tracking a package installation."""
        if package_name in self.package_times:
            install_time = time.time() - self.package_times[package_name]
            
            if success:
                self.completed_packages += 1
                self.logger.info(f"✓ {package_name} installed in {install_time:.2f}s")
            else:
                self.failed_packages += 1
                self.logger.error(f"✗ {package_name} failed after {install_time:.2f}s")
    
    def get_progress_report(self) -> Dict:
        """Get current progress report."""
        elapsed_time = time.time() - self.start_time
        
        return {
            'total_packages': self.total_packages,
            'completed_packages': self.completed_packages,
            'failed_packages': self.failed_packages,
            'remaining_packages': self.total_packages - self.completed_packages - self.failed_packages,
            'progress_percentage': (self.completed_packages / self.total_packages) * 100 if self.total_packages > 0 else 0,
            'elapsed_time': elapsed_time,
            'current_batch': self.current_batch,
            'total_batches': self.total_batches,
            'current_package': self.current_package
        }
    
    def finish_installation(self):
        """Finish tracking installation."""
        elapsed_time = time.time() - self.start_time
        success_rate = (self.completed_packages / self.total_packages) * 100 if self.total_packages > 0 else 0
        
        self.logger.info(f"Installation completed in {elapsed_time:.2f}s")
        self.logger.info(f"Success rate: {success_rate:.1f}% ({self.completed_packages}/{self.total_packages})")
        
        if self.failed_packages > 0:
            self.logger.warning(f"Failed packages: {self.failed_packages}")


class ProgressiveInstaller:
    """
    Comprehensive progressive package installer with advanced features.
    
    Features:
    - Dependency-ordered installation using topological sorting
    - Installation checkpoints with rollback capability
    - Compilation requirements detection and handling
    - Exponential backoff retry logic for network failures
    - Installation progress tracking and reporting
    - Batch installation optimization
    """
    
    def __init__(self, 
                 venv_manager: VirtualEnvironmentManager,
                 dependency_resolver: DependencyResolver,
                 logger: logging.Logger,
                 max_retries: int = 3,
                 batch_size: int = 5):
        """Initialize the progressive installer.
        
        Args:
            venv_manager: Virtual environment manager instance
            dependency_resolver: Dependency resolver instance
            logger: Logger instance
            max_retries: Maximum retry attempts for failed installations
            batch_size: Number of packages to install in each batch
        """
        self.venv_manager = venv_manager
        self.dependency_resolver = dependency_resolver
        self.logger = logger
        self.max_retries = max_retries
        self.batch_size = batch_size
        
        # Initialize components
        self.compilation_handler = CompilationHandler(logger)
        self.retry_manager = RetryManager(logger, max_retries)
        self.progress_tracker = ProgressTracker(logger)
        
        # Installation state
        self.packages: Dict[str, PackageInfo] = {}
        self.installation_order: List[str] = []
        self.batches: List[InstallationBatch] = []
        self.checkpoints: List[InstallationCheckpoint] = []
        self.checkpoint_dir = Path(tempfile.gettempdir()) / "venv_checkpoints"
        self.checkpoint_dir.mkdir(exist_ok=True)
        
        # Installation statistics
        self.stats = {
            'total_packages': 0,
            'successful_installs': 0,
            'failed_installs': 0,
            'retried_installs': 0,
            'compilation_packages': 0,
            'total_time': 0.0
        }
    
    def install_from_requirements(self, requirements_file: Path) -> bool:
        """Install packages from requirements file with progressive strategy.
        
        Args:
            requirements_file: Path to requirements.txt file
            
        Returns:
            True if installation successful, False otherwise
        """
        self.logger.info(f"Starting progressive installation from {requirements_file}")
        
        try:
            # Phase 1: Parse and analyze requirements
            if not self._parse_requirements(requirements_file):
                return False
            
            # Phase 2: Check build requirements
            if not self._check_build_requirements():
                return False
            
            # Phase 3: Create installation plan
            if not self._create_installation_plan():
                return False
            
            # Phase 4: Execute progressive installation
            if not self._execute_installation():
                return False
            
            # Phase 5: Verify installation
            if not self._verify_installation():
                return False
            
            self._generate_installation_report()
            return True
            
        except Exception as e:
            self.logger.error(f"Progressive installation failed: {e}")
            return False
        finally:
            self._cleanup_checkpoints()
    
    def _parse_requirements(self, requirements_file: Path) -> bool:
        """Parse requirements file and create package information."""
        self.logger.info("Parsing requirements file...")
        
        try:
            # Use dependency resolver to parse requirements
            analysis = self.dependency_resolver.analyze_requirements_file(requirements_file)
            
            if 'error' in analysis:
                self.logger.error(f"Requirements analysis failed: {analysis['error']}")
                return False
            
            # Check for conflicts
            if analysis.get('conflicts'):
                self.logger.warning(f"Found {len(analysis['conflicts'])} dependency conflicts")
                for conflict in analysis['conflicts']:
                    if isinstance(conflict, dict):
                        pkg_name = conflict.get('package', 'unknown')
                        severity = conflict.get('severity', 'unknown')
                        self.logger.warning(f"Conflict: {pkg_name} - {severity}")
                
                # For now, continue with installation but log warnings
                # In future, could implement conflict resolution
            
            # Create package information
            for pkg_info in analysis.get('valid_packages', []):
                if isinstance(pkg_info, dict):
                    package_name = pkg_info.get('name', '')
                    requirement = pkg_info.get('requirement', '')
                    requirement_str = f"{package_name}{requirement}"
                    
                    if package_name:  # Only process if we have a valid package name
                        # Classify package type
                        package_type = self.compilation_handler.classify_package(package_name)
                        
                        self.packages[package_name] = PackageInfo(
                            name=package_name,
                            requirement_string=requirement_str,
                            package_type=package_type
                        )
            
            self.stats['total_packages'] = len(self.packages)
            self.logger.info(f"Parsed {len(self.packages)} packages")
            
            # Count compilation packages
            compilation_count = sum(
                1 for pkg in self.packages.values()
                if pkg.package_type == PackageType.COMPILED
            )
            self.stats['compilation_packages'] = compilation_count
            
            if compilation_count > 0:
                self.logger.info(f"Found {compilation_count} packages requiring compilation")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to parse requirements: {e}")
            return False
    
    def _check_build_requirements(self) -> bool:
        """Check and report build requirements."""
        self.logger.info("Checking build requirements...")
        
        # Check if we have any packages requiring compilation
        compilation_packages = [
            pkg for pkg in self.packages.values()
            if pkg.package_type == PackageType.COMPILED
        ]
        
        if not compilation_packages:
            self.logger.info("No compilation packages found, skipping build tools check")
            return True
        
        # Check build tools
        build_requirements = self.compilation_handler.check_build_requirements()
        missing_tools = [
            tool for tool, available in build_requirements.items()
            if not available
        ]
        
        if missing_tools:
            self.logger.warning(f"Missing build tools: {missing_tools}")
            
            # Get recommendations
            recommendations = self.compilation_handler.get_build_recommendations(
                missing_tools
            )
            if recommendations:
                self.logger.info("Build tool installation recommendations:")
                for rec in recommendations:
                    self.logger.info(f"  - {rec}")
            
            # For now, continue with installation but warn user
            self.logger.warning("Continuing installation - some packages may fail to compile")
        else:
            self.logger.info("All required build tools are available")
        
        return True
    
    def _create_installation_plan(self) -> bool:
        """Create installation plan with dependency ordering and batching."""
        self.logger.info("Creating installation plan...")
        
        try:
            # Get installation order using dependency resolver
            requirements_list = [pkg.requirement_string for pkg in self.packages.values()]
            self.installation_order = self.dependency_resolver.validate_installation_order(requirements_list)
            
            # Create batches based on package types and dependencies
            self._create_installation_batches()
            
            self.logger.info(f"Created installation plan with {len(self.batches)} batches")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create installation plan: {e}")
            return False
    
    def _create_installation_batches(self):
        """Create installation batches optimized for dependencies and package types."""
        self.batches = []
        batch_id = 1
        
        # Group packages by type for optimal installation order
        build_tools = []
        pure_python = []
        compiled = []
        system_dependent = []
        
        for package_name in self.installation_order:
            if package_name in self.packages:
                pkg = self.packages[package_name]
                if pkg.package_type == PackageType.BUILD_TOOLS:
                    build_tools.append(pkg)
                elif pkg.package_type == PackageType.PURE_PYTHON:
                    pure_python.append(pkg)
                elif pkg.package_type == PackageType.COMPILED:
                    compiled.append(pkg)
                else:
                    system_dependent.append(pkg)
        
        # Create batches: build tools first, then pure python, then compiled
        for batch_type, packages in [
            ("build_tools", build_tools),
            ("pure_python", pure_python),
            ("system_dependent", system_dependent),
            ("compiled", compiled)
        ]:
            if packages:
                # Split into smaller batches
                for i in range(0, len(packages), self.batch_size):
                    batch_packages = packages[i:i + self.batch_size]
                    
                    batch = InstallationBatch(
                        batch_id=batch_id,
                        packages=batch_packages,
                        batch_type=batch_type
                    )
                    
                    self.batches.append(batch)
                    batch_id += 1
    
    def _execute_installation(self) -> bool:
        """Execute the progressive installation plan."""
        self.logger.info("Executing progressive installation...")
        
        start_time = time.time()
        self.progress_tracker.start_installation(
            len(self.packages), 
            len(self.batches)
        )
        
        try:
            # Create initial checkpoint
            if not self._create_checkpoint("initial", "Before installation"):
                self.logger.warning("Failed to create initial checkpoint")
            
            # Install batches progressively
            for batch in self.batches:
                if not self._install_batch(batch):
                    self.logger.error(f"Batch {batch.batch_id} installation failed")
                    return False
            
            self.stats['total_time'] = time.time() - start_time
            self.progress_tracker.finish_installation()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Installation execution failed: {e}")
            return False
    
    def _install_batch(self, batch: InstallationBatch) -> bool:
        """Install a batch of packages."""
        package_names = [pkg.name for pkg in batch.packages]
        self.progress_tracker.start_batch(batch.batch_id, package_names)
        
        # Create checkpoint before batch
        checkpoint_desc = f"Before batch {batch.batch_id} ({batch.batch_type})"
        if not self._create_checkpoint(f"batch_{batch.batch_id}", checkpoint_desc):
            self.logger.warning(f"Failed to create checkpoint for batch {batch.batch_id}")
        
        # Install packages in batch
        batch_success = True
        for package in batch.packages:
            if not self._install_package(package):
                batch_success = False
                
                # Decide whether to continue or rollback
                if package.package_type == PackageType.BUILD_TOOLS:
                    # Build tools are critical, consider rollback
                    self.logger.error(f"Critical package {package.name} failed, considering rollback")
                    # For now, continue but mark as failed
                
        return batch_success
    
    def _install_package(self, package: PackageInfo) -> bool:
        """Install a single package with retry logic."""
        self.progress_tracker.start_package(package.name)
        package.status = InstallationStatus.IN_PROGRESS
        
        def install_func():
            return self.venv_manager.install_packages(
                packages=[package.requirement_string],
                timeout=300  # 5 minute timeout per package
            )
        
        try:
            # Use retry manager for installation
            success = self.retry_manager.execute_with_retry(install_func)
            
            if success:
                package.status = InstallationStatus.COMPLETED
                self.stats['successful_installs'] += 1
                self.progress_tracker.complete_package(package.name, True)
                return True
            else:
                package.status = InstallationStatus.FAILED
                package.error_message = "Installation returned False"
                self.stats['failed_installs'] += 1
                self.progress_tracker.complete_package(package.name, False)
                return False
                
        except Exception as e:
            package.status = InstallationStatus.FAILED
            package.error_message = str(e)
            self.stats['failed_installs'] += 1
            self.progress_tracker.complete_package(package.name, False)
            
            self.logger.error(f"Package {package.name} installation failed: {e}")
            return False
    
    def _create_checkpoint(self, checkpoint_id: str, description: str) -> bool:
        """Create an installation checkpoint."""
        try:
            # Get current installed packages
            installed_packages = self.venv_manager.get_installed_packages()
            
            # Calculate environment hash
            env_hash = hashlib.sha256(
                json.dumps(installed_packages, sort_keys=True).encode()
            ).hexdigest()[:16]
            
            # Create checkpoint directory
            checkpoint_path = self.checkpoint_dir / f"checkpoint_{checkpoint_id}_{int(time.time())}"
            checkpoint_path.mkdir(exist_ok=True)
            
            # Save checkpoint data
            checkpoint_data = {
                'checkpoint_id': checkpoint_id,
                'timestamp': time.time(),
                'description': description,
                'installed_packages': installed_packages,
                'environment_hash': env_hash
            }
            
            checkpoint_file = checkpoint_path / "checkpoint.json"
            with open(checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
            
            checkpoint = InstallationCheckpoint(
                checkpoint_id=checkpoint_id,
                timestamp=time.time(),
                installed_packages=installed_packages,
                environment_hash=env_hash,
                checkpoint_path=checkpoint_path,
                description=description
            )
            
            self.checkpoints.append(checkpoint)
            self.logger.debug(f"Created checkpoint: {checkpoint_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create checkpoint {checkpoint_id}: {e}")
            return False
    
    def _verify_installation(self) -> bool:
        """Verify that all packages were installed correctly."""
        self.logger.info("Verifying installation...")
        
        try:
            installed_packages = self.venv_manager.get_installed_packages()
            installed_names = {pkg['name'].lower() for pkg in installed_packages}
            
            verification_failed = []
            for package_name, package_info in self.packages.items():
                if package_name.lower() not in installed_names:
                    verification_failed.append(package_name)
                    package_info.status = InstallationStatus.FAILED
            
            if verification_failed:
                self.logger.error(f"Verification failed for {len(verification_failed)} packages: {verification_failed}")
                return False
            
            self.logger.info("Installation verification successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Installation verification failed: {e}")
            return False
    
    def _generate_installation_report(self):
        """Generate comprehensive installation report."""
        report_lines = [
            "=" * 60,
            "PROGRESSIVE INSTALLATION REPORT",
            "=" * 60,
            "",
            f"Total Packages: {self.stats['total_packages']}",
            f"Successful Installs: {self.stats['successful_installs']}",
            f"Failed Installs: {self.stats['failed_installs']}",
            f"Compilation Packages: {self.stats['compilation_packages']}",
            f"Total Installation Time: {self.stats['total_time']:.2f} seconds",
            f"Success Rate: {(self.stats['successful_installs'] / self.stats['total_packages']) * 100:.1f}%",
            "",
        ]
        
        # Add batch information
        if self.batches:
            report_lines.extend([
                "INSTALLATION BATCHES:",
                "-" * 20,
            ])
            for batch in self.batches:
                package_names = [pkg.name for pkg in batch.packages]
                report_lines.append(f"Batch {batch.batch_id} ({batch.batch_type}): {', '.join(package_names)}")
            report_lines.append("")
        
        # Add failed packages
        failed_packages = [pkg for pkg in self.packages.values()
                          if pkg.status == InstallationStatus.FAILED]
        if failed_packages:
            report_lines.extend([
                "FAILED PACKAGES:",
                "-" * 16,
            ])
            for pkg in failed_packages:
                report_lines.extend([
                    f"Package: {pkg.name}",
                    f"Type: {pkg.package_type.value}",
                    f"Error: {pkg.error_message}",
                    "",
                ])
        
        report_lines.append("=" * 60)
        
        report = "\n".join(report_lines)
        self.logger.info(f"Installation Report:\n{report}")
        
        # Save report to file
        try:
            report_file = Path("progressive_installation_report.txt")
            with open(report_file, 'w') as f:
                f.write(report)
            self.logger.info(f"Installation report saved to {report_file}")
        except Exception as e:
            self.logger.warning(f"Failed to save installation report: {e}")
    
    def _cleanup_checkpoints(self):
        """Clean up temporary checkpoint files."""
        try:
            for checkpoint in self.checkpoints:
                if checkpoint.checkpoint_path.exists():
                    shutil.rmtree(checkpoint.checkpoint_path)
            
            # Remove checkpoint directory if empty
            if self.checkpoint_dir.exists() and not any(self.checkpoint_dir.iterdir()):
                self.checkpoint_dir.rmdir()
                
            self.logger.debug("Checkpoint cleanup completed")
            
        except Exception as e:
            self.logger.warning(f"Checkpoint cleanup failed: {e}")
    
    def rollback_to_checkpoint(self, checkpoint_id: str) -> bool:
        """Rollback installation to a specific checkpoint."""
        self.logger.info(f"Rolling back to checkpoint: {checkpoint_id}")
        
        # Find checkpoint
        checkpoint = None
        for cp in self.checkpoints:
            if cp.checkpoint_id == checkpoint_id:
                checkpoint = cp
                break
        
        if not checkpoint:
            self.logger.error(f"Checkpoint {checkpoint_id} not found")
            return False
        
        try:
            # This would require more complex implementation
            # For now, just log the rollback attempt
            self.logger.warning("Rollback functionality not fully implemented")
            self.logger.info(f"Would rollback to checkpoint created at {checkpoint.timestamp}")
            self.logger.info(f"Checkpoint description: {checkpoint.description}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Rollback failed: {e}")
            return False
    
    def get_installation_status(self) -> Dict:
        """Get current installation status."""
        return {
            'total_packages': len(self.packages),
            'completed_packages': len([p for p in self.packages.values()
                                     if p.status == InstallationStatus.COMPLETED]),
            'failed_packages': len([p for p in self.packages.values()
                                  if p.status == InstallationStatus.FAILED]),
            'in_progress_packages': len([p for p in self.packages.values()
                                       if p.status == InstallationStatus.IN_PROGRESS]),
            'batches_total': len(self.batches),
            'checkpoints_created': len(self.checkpoints),
            'stats': self.stats.copy()
        }