#!/usr/bin/env python3
"""Cross-Platform Package Installation Automation.

This module provides comprehensive cross-platform package installation
automation with support for Windows, Linux, and macOS package managers.
"""

import logging
import os
import platform
import shutil
import subprocess
import sys
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class PackageInfo:
    """Information about a package."""

    name: str
    version: Optional[str] = None
    description: Optional[str] = ""
    dependencies: Optional[List[str]] = None
    platform_specific: bool = False

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class InstallationResult:
    """Result of package installation."""

    package: str
    success: bool
    message: str
    installation_time: float
    log_output: str = ""


class PackageManager(ABC):
    """Abstract base class for package managers."""

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"PackageManager.{name}")

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this package manager is available on the system."""
        pass

    @abstractmethod
    def install_package(self, package: PackageInfo) -> InstallationResult:
        """Install a package using this package manager."""
        pass

    @abstractmethod
    def check_package_installed(self, package_name: str) -> bool:
        """Check if a package is already installed."""
        pass

    @abstractmethod
    def get_installed_version(self, package_name: str) -> Optional[str]:
        """Get the installed version of a package."""
        pass


class PipPackageManager(PackageManager):
    """Python pip package manager."""

    def __init__(self):
        super().__init__("pip")

    def is_available(self) -> bool:
        """Check if pip is available."""
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                check=True,
                capture_output=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def install_package(self, package: PackageInfo) -> InstallationResult:
        """Install a Python package using pip."""
        start_time = time.time()
        package_spec = package.name
        if package.version:
            package_spec += f"=={package.version}"

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--upgrade",
                    package_spec,
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )

            installation_time = time.time() - start_time

            if result.returncode == 0:
                return InstallationResult(
                    package=package.name,
                    success=True,
                    message=f"Successfully installed {package_spec}",
                    installation_time=installation_time,
                    log_output=result.stdout,
                )
            else:
                return InstallationResult(
                    package=package.name,
                    success=False,
                    message=f"Failed to install {package_spec}: {result.stderr}",
                    installation_time=installation_time,
                    log_output=result.stderr,
                )

        except subprocess.TimeoutExpired:
            return InstallationResult(
                package=package.name,
                success=False,
                message=f"Installation of {package_spec} timed out",
                installation_time=time.time() - start_time,
            )
        except Exception as e:
            return InstallationResult(
                package=package.name,
                success=False,
                message=f"Error installing {package_spec}: {str(e)}",
                installation_time=time.time() - start_time,
            )

    def check_package_installed(self, package_name: str) -> bool:
        """Check if a Python package is installed."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", package_name],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except:
            return False

    def get_installed_version(self, package_name: str) -> Optional[str]:
        """Get the installed version of a Python package."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", package_name],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if line.startswith("Version:"):
                        return line.split(":", 1)[1].strip()
            return None
        except:
            return None


class AptPackageManager(PackageManager):
    """Ubuntu/Debian APT package manager with enhanced distribution support."""

    def __init__(self):
        super().__init__("apt")
        self.distribution_info = self._detect_distribution()
        self.package_mapping = self._load_distribution_package_mapping()

    def _detect_distribution(self) -> Dict[str, str]:
        """Detect specific Linux distribution information."""
        dist_info = {}

        try:
            # Read /etc/os-release for modern distributions
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if "=" in line:
                        key, value = line.strip().split("=", 1)
                        dist_info[key] = value.strip('"')
        except FileNotFoundError:
            pass

        # Fallback methods for older distributions
        try:
            # Check for lsb_release
            result = subprocess.run(
                ["lsb_release", "-a"], capture_output=True, text=True
            )
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        dist_info[f"LSB_{key.strip()}"] = value.strip()
        except (FileNotFoundError, subprocess.SubprocessError):
            pass

        # Check specific distribution files
        distribution_files = {
            "debian": "/etc/debian_version",
            "ubuntu": "/etc/lsb-release",
            "mint": "/etc/linuxmint/info",
            "elementary": "/etc/lsb-release",
        }

        for dist_name, file_path in distribution_files.items():
            if os.path.exists(file_path):
                dist_info["detected_distribution"] = dist_name
                break

        return dist_info

    def _load_distribution_package_mapping(self) -> Dict[str, Dict[str, str]]:
        """Load package name mappings for different distributions."""
        return {
            "visualization": {
                "matplotlib": {
                    "ubuntu": "python3-matplotlib",
                    "debian": "python3-matplotlib",
                    "mint": "python3-matplotlib",
                    "elementary": "python3-matplotlib",
                },
                "numpy": {
                    "ubuntu": "python3-numpy",
                    "debian": "python3-numpy",
                    "mint": "python3-numpy",
                    "elementary": "python3-numpy",
                },
            },
            "network": {
                "net-tools": {
                    "ubuntu": "net-tools",
                    "debian": "net-tools",
                    "mint": "net-tools",
                    "elementary": "net-tools",
                },
                "wireless-tools": {
                    "ubuntu": "wireless-tools",
                    "debian": "wireless-tools",
                    "mint": "wireless-tools",
                    "elementary": "wireless-tools",
                },
            },
        }

    def is_available(self) -> bool:
        """Check if apt is available."""
        return (
            shutil.which("apt") is not None
            or shutil.which("apt-get") is not None
        )

    def install_package(self, package: PackageInfo) -> InstallationResult:
        """Install a package using apt."""
        start_time = time.time()

        try:
            # Update package list first
            subprocess.run(
                ["sudo", "apt", "update"], check=True, capture_output=True
            )

            # Install package
            result = subprocess.run(
                ["sudo", "apt", "install", "-y", package.name],
                capture_output=True,
                text=True,
                timeout=600,
            )

            installation_time = time.time() - start_time

            if result.returncode == 0:
                return InstallationResult(
                    package=package.name,
                    success=True,
                    message=f"Successfully installed {package.name}",
                    installation_time=installation_time,
                    log_output=result.stdout,
                )
            else:
                return InstallationResult(
                    package=package.name,
                    success=False,
                    message=f"Failed to install {package.name}: {result.stderr}",
                    installation_time=installation_time,
                    log_output=result.stderr,
                )

        except subprocess.TimeoutExpired:
            return InstallationResult(
                package=package.name,
                success=False,
                message=f"Installation of {package.name} timed out",
                installation_time=time.time() - start_time,
            )
        except Exception as e:
            return InstallationResult(
                package=package.name,
                success=False,
                message=f"Error installing {package.name}: {str(e)}",
                installation_time=time.time() - start_time,
            )

    def check_package_installed(self, package_name: str) -> bool:
        """Check if a package is installed via apt."""
        try:
            result = subprocess.run(
                ["dpkg", "-l", package_name], capture_output=True, text=True
            )
            return result.returncode == 0 and "ii" in result.stdout
        except:
            return False

    def get_installed_version(self, package_name: str) -> Optional[str]:
        """Get the installed version of an apt package."""
        try:
            result = subprocess.run(
                ["dpkg", "-l", package_name], capture_output=True, text=True
            )

            if result.returncode == 0:
                lines = result.stdout.split("\n")
                for line in lines:
                    if line.startswith("ii") and package_name in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            return parts[2]
            return None
        except:
            return None


class YumPackageManager(PackageManager):
    """CentOS/RHEL YUM package manager."""

    def __init__(self):
        super().__init__("yum")

    def is_available(self) -> bool:
        """Check if yum is available."""
        return (
            shutil.which("yum") is not None or shutil.which("dnf") is not None
        )

    def install_package(self, package: PackageInfo) -> InstallationResult:
        """Install a package using yum/dnf."""
        start_time = time.time()

        # Prefer dnf over yum if available
        cmd = "dnf" if shutil.which("dnf") else "yum"

        try:
            result = subprocess.run(
                ["sudo", cmd, "install", "-y", package.name],
                capture_output=True,
                text=True,
                timeout=600,
            )

            installation_time = time.time() - start_time

            if result.returncode == 0:
                return InstallationResult(
                    package=package.name,
                    success=True,
                    message=f"Successfully installed {package.name}",
                    installation_time=installation_time,
                    log_output=result.stdout,
                )
            else:
                return InstallationResult(
                    package=package.name,
                    success=False,
                    message=f"Failed to install {package.name}: {result.stderr}",
                    installation_time=installation_time,
                    log_output=result.stderr,
                )

        except subprocess.TimeoutExpired:
            return InstallationResult(
                package=package.name,
                success=False,
                message=f"Installation of {package.name} timed out",
                installation_time=time.time() - start_time,
            )
        except Exception as e:
            return InstallationResult(
                package=package.name,
                success=False,
                message=f"Error installing {package.name}: {str(e)}",
                installation_time=time.time() - start_time,
            )

    def check_package_installed(self, package_name: str) -> bool:
        """Check if a package is installed via yum/dnf."""
        cmd = "dnf" if shutil.which("dnf") else "yum"
        try:
            result = subprocess.run(
                [cmd, "list", "installed", package_name],
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except:
            return False

    def get_installed_version(self, package_name: str) -> Optional[str]:
        """Get the installed version of a yum/dnf package."""
        cmd = "dnf" if shutil.which("dnf") else "yum"
        try:
            result = subprocess.run(
                [cmd, "list", "installed", package_name],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                lines = result.stdout.split("\n")
                for line in lines:
                    if package_name in line and "." in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            return parts[1].split(".")[0]
            return None
        except:
            return None


class HomebrewPackageManager(PackageManager):
    """macOS Homebrew package manager."""

    def __init__(self):
        super().__init__("homebrew")

    def is_available(self) -> bool:
        """Check if Homebrew is available."""
        return shutil.which("brew") is not None

    def install_package(self, package: PackageInfo) -> InstallationResult:
        """Install a package using Homebrew."""
        start_time = time.time()

        try:
            result = subprocess.run(
                ["brew", "install", package.name],
                capture_output=True,
                text=True,
                timeout=600,
            )

            installation_time = time.time() - start_time

            if result.returncode == 0:
                return InstallationResult(
                    package=package.name,
                    success=True,
                    message=f"Successfully installed {package.name}",
                    installation_time=installation_time,
                    log_output=result.stdout,
                )
            else:
                return InstallationResult(
                    package=package.name,
                    success=False,
                    message=f"Failed to install {package.name}: {result.stderr}",
                    installation_time=installation_time,
                    log_output=result.stderr,
                )

        except subprocess.TimeoutExpired:
            return InstallationResult(
                package=package.name,
                success=False,
                message=f"Installation of {package.name} timed out",
                installation_time=time.time() - start_time,
            )
        except Exception as e:
            return InstallationResult(
                package=package.name,
                success=False,
                message=f"Error installing {package.name}: {str(e)}",
                installation_time=time.time() - start_time,
            )

    def check_package_installed(self, package_name: str) -> bool:
        """Check if a package is installed via Homebrew."""
        try:
            result = subprocess.run(
                ["brew", "list", package_name], capture_output=True, text=True
            )
            return result.returncode == 0
        except:
            return False

    def get_installed_version(self, package_name: str) -> Optional[str]:
        """Get the installed version of a Homebrew package."""
        try:
            result = subprocess.run(
                ["brew", "list", "--versions", package_name],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                # Output format: "package_name version"
                parts = result.stdout.strip().split()
                if len(parts) >= 2:
                    return parts[1]
            return None
        except:
            return None


class CrossPlatformPackageInstaller:
    """Cross-platform package installation automation."""

    def __init__(self, verbose: bool = False):
        """Initialize the cross-platform package installer.

        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.setup_logging()

        # Detect platform and available package managers
        self.platform = platform.system().lower()
        self.package_managers = self._detect_package_managers()

        # Installation statistics
        self.installation_stats = {
            "total_packages": 0,
            "successful_installations": 0,
            "failed_installations": 0,
            "already_installed": 0,
            "total_time": 0.0,
        }

        # Package definitions
        self.package_definitions = self._load_package_definitions()

        self.logger.info(f"CrossPlatformPackageInstaller initialized")
        self.logger.info(f"Platform: {self.platform}")
        self.logger.info(
            f"Available package managers: {[pm.name for pm in self.package_managers]}"
        )

    def setup_logging(self):
        """Setup logging configuration."""
        log_level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(
                    f'package_installation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
                ),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def _detect_package_managers(self) -> List[PackageManager]:
        """Detect available package managers on the system."""
        managers = []

        # Always include pip for Python packages
        pip_manager = PipPackageManager()
        if pip_manager.is_available():
            managers.append(pip_manager)

        # Platform-specific package managers
        if self.platform == "linux":
            # APT (Ubuntu/Debian)
            apt_manager = AptPackageManager()
            if apt_manager.is_available():
                managers.append(apt_manager)

            # YUM/DNF (CentOS/RHEL/Fedora)
            yum_manager = YumPackageManager()
            if yum_manager.is_available():
                managers.append(yum_manager)

        elif self.platform == "darwin":  # macOS
            # Homebrew
            brew_manager = HomebrewPackageManager()
            if brew_manager.is_available():
                managers.append(brew_manager)

        # Windows package managers would go here (Chocolatey, winget, etc.)

        return managers

    def _load_package_definitions(self) -> Dict[str, Dict]:
        """Load package definitions for different platforms."""
        return {
            "visualization": {
                "matplotlib": {
                    "pip": PackageInfo(
                        "matplotlib", "3.7.0", "Python plotting library"
                    ),
                    "apt": PackageInfo(
                        "python3-matplotlib",
                        description="Matplotlib for Python 3",
                    ),
                    "yum": PackageInfo(
                        "python3-matplotlib",
                        description="Matplotlib for Python 3",
                    ),
                    "homebrew": PackageInfo(
                        "matplotlib", description="Python plotting library"
                    ),
                },
                "numpy": {
                    "pip": PackageInfo(
                        "numpy", "1.24.0", "Numerical computing library"
                    ),
                    "apt": PackageInfo(
                        "python3-numpy", description="NumPy for Python 3"
                    ),
                    "yum": PackageInfo(
                        "python3-numpy", description="NumPy for Python 3"
                    ),
                    "homebrew": PackageInfo(
                        "numpy", description="Numerical computing library"
                    ),
                },
                "seaborn": {
                    "pip": PackageInfo(
                        "seaborn", "0.12.0", "Statistical data visualization"
                    ),
                    "apt": PackageInfo(
                        "python3-seaborn", description="Seaborn for Python 3"
                    ),
                    "yum": PackageInfo(
                        "python3-seaborn", description="Seaborn for Python 3"
                    ),
                    "homebrew": PackageInfo(
                        "seaborn", description="Statistical data visualization"
                    ),
                },
                "plotly": {
                    "pip": PackageInfo(
                        "plotly", "5.15.0", "Interactive plotting library"
                    ),
                    "apt": PackageInfo(
                        "python3-plotly", description="Plotly for Python 3"
                    ),
                    "yum": PackageInfo(
                        "python3-plotly", description="Plotly for Python 3"
                    ),
                    "homebrew": PackageInfo(
                        "plotly", description="Interactive plotting library"
                    ),
                },
                "bokeh": {
                    "pip": PackageInfo(
                        "bokeh", "3.0.0", "Interactive visualization library"
                    ),
                    "apt": PackageInfo(
                        "python3-bokeh", description="Bokeh for Python 3"
                    ),
                    "yum": PackageInfo(
                        "python3-bokeh", description="Bokeh for Python 3"
                    ),
                    "homebrew": PackageInfo(
                        "bokeh",
                        description="Interactive visualization library",
                    ),
                },
                "dash": {
                    "pip": PackageInfo(
                        "dash", "2.10.0", "Web application framework"
                    ),
                    "apt": PackageInfo(
                        "python3-dash", description="Dash for Python 3"
                    ),
                    "yum": PackageInfo(
                        "python3-dash", description="Dash for Python 3"
                    ),
                    "homebrew": PackageInfo(
                        "dash", description="Web application framework"
                    ),
                },
            },
            "scientific": {
                "scipy": {
                    "pip": PackageInfo(
                        "scipy", "1.10.0", "Scientific computing library"
                    ),
                    "apt": PackageInfo(
                        "python3-scipy", description="SciPy for Python 3"
                    ),
                    "yum": PackageInfo(
                        "python3-scipy", description="SciPy for Python 3"
                    ),
                    "homebrew": PackageInfo(
                        "scipy", description="Scientific computing library"
                    ),
                },
                "pandas": {
                    "pip": PackageInfo(
                        "pandas", "2.0.0", "Data analysis library"
                    ),
                    "apt": PackageInfo(
                        "python3-pandas", description="Pandas for Python 3"
                    ),
                    "yum": PackageInfo(
                        "python3-pandas", description="Pandas for Python 3"
                    ),
                    "homebrew": PackageInfo(
                        "pandas", description="Data analysis library"
                    ),
                },
                "scikit-learn": {
                    "pip": PackageInfo(
                        "scikit-learn", "1.3.0", "Machine learning library"
                    ),
                    "apt": PackageInfo(
                        "python3-sklearn",
                        description="Scikit-learn for Python 3",
                    ),
                    "yum": PackageInfo(
                        "python3-scikit-learn",
                        description="Scikit-learn for Python 3",
                    ),
                    "homebrew": PackageInfo(
                        "scikit-learn", description="Machine learning library"
                    ),
                },
            },
            "network": {
                "networkx": {
                    "pip": PackageInfo(
                        "networkx", "3.0", "Network analysis library"
                    ),
                    "apt": PackageInfo(
                        "python3-networkx", description="NetworkX for Python 3"
                    ),
                    "yum": PackageInfo(
                        "python3-networkx", description="NetworkX for Python 3"
                    ),
                    "homebrew": PackageInfo(
                        "networkx", description="Network analysis library"
                    ),
                },
                "igraph": {
                    "pip": PackageInfo(
                        "python-igraph", "0.10.0", "Graph analysis library"
                    ),
                    "apt": PackageInfo(
                        "python3-igraph", description="IGraph for Python 3"
                    ),
                    "yum": PackageInfo(
                        "python3-igraph", description="IGraph for Python 3"
                    ),
                    "homebrew": PackageInfo(
                        "python-igraph", description="Graph analysis library"
                    ),
                },
            },
        }

    def get_package_for_manager(
        self, package_name: str, manager: PackageManager
    ) -> Optional[PackageInfo]:
        """Get package info for a specific package manager."""
        for category in self.package_definitions.values():
            if package_name in category:
                package_dict = category[package_name]
                if manager.name in package_dict:
                    return package_dict[manager.name]
        return None

    def install_package(
        self, package_name: str, preferred_manager: Optional[str] = None
    ) -> InstallationResult:
        """Install a single package.

        Args:
            package_name: Name of the package to install
            preferred_manager: Preferred package manager to use

        Returns:
            InstallationResult with installation details
        """
        self.logger.info(f"Installing package: {package_name}")

        # Find appropriate package manager
        target_manager = None

        if preferred_manager:
            for manager in self.package_managers:
                if manager.name == preferred_manager:
                    target_manager = manager
                    break

        if not target_manager:
            # Use the first available manager that supports this package
            for manager in self.package_managers:
                package_info = self.get_package_for_manager(
                    package_name, manager
                )
                if package_info:
                    target_manager = manager
                    break

        if not target_manager:
            return InstallationResult(
                package=package_name,
                success=False,
                message=f"No suitable package manager found for {package_name}",
                installation_time=0.0,
            )

        # Get package info for the selected manager
        package_info = self.get_package_for_manager(
            package_name, target_manager
        )
        if not package_info:
            return InstallationResult(
                package=package_name,
                success=False,
                message=f"Package {package_name} not defined for {target_manager.name}",
                installation_time=0.0,
            )

        # Check if already installed
        if target_manager.check_package_installed(package_info.name):
            installed_version = target_manager.get_installed_version(
                package_info.name
            )
            self.logger.info(
                f"Package {package_name} already installed (version: {installed_version})"
            )
            self.installation_stats["already_installed"] += 1
            return InstallationResult(
                package=package_name,
                success=True,
                message=f"Package {package_name} already installed (version: {installed_version})",
                installation_time=0.0,
            )

        # Install the package
        result = target_manager.install_package(package_info)

        # Update statistics
        self.installation_stats["total_packages"] += 1
        self.installation_stats["total_time"] += result.installation_time

        if result.success:
            self.installation_stats["successful_installations"] += 1
            self.logger.info(f"Successfully installed {package_name}")
        else:
            self.installation_stats["failed_installations"] += 1
            self.logger.error(
                f"Failed to install {package_name}: {result.message}"
            )

        return result

    def install_packages(
        self,
        package_names: List[str],
        parallel: bool = True,
        max_workers: int = 4,
    ) -> List[InstallationResult]:
        """Install multiple packages.

        Args:
            package_names: List of package names to install
            parallel: Whether to install packages in parallel
            max_workers: Maximum number of parallel workers

        Returns:
            List of InstallationResult objects
        """
        self.logger.info(f"Installing {len(package_names)} packages")
        results = []

        if parallel and len(package_names) > 1:
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor(
                max_workers=max_workers
            ) as executor:
                future_to_package = {
                    executor.submit(
                        self.install_package, package_name
                    ): package_name
                    for package_name in package_names
                }

                for future in concurrent.futures.as_completed(
                    future_to_package
                ):
                    package_name = future_to_package[future]
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        self.logger.error(
                            f"Exception installing {package_name}: {e}"
                        )
                        results.append(
                            InstallationResult(
                                package=package_name,
                                success=False,
                                message=f"Exception during installation: {str(e)}",
                                installation_time=0.0,
                            )
                        )
        else:
            # Sequential installation
            for package_name in package_names:
                result = self.install_package(package_name)
                results.append(result)

        return results

    def install_visualization_packages(self) -> List[InstallationResult]:
        """Install all visualization packages."""
        package_names = list(self.package_definitions["visualization"].keys())
        return self.install_packages(package_names)

    def install_scientific_packages(self) -> List[InstallationResult]:
        """Install all scientific computing packages."""
        package_names = list(self.package_definitions["scientific"].keys())
        return self.install_packages(package_names)

    def install_network_packages(self) -> List[InstallationResult]:
        """Install all network analysis packages."""
        package_names = list(self.package_definitions["network"].keys())
        return self.install_packages(package_names)

    def install_all_packages(self) -> List[InstallationResult]:
        """Install all available packages."""
        all_packages = []
        for category in self.package_definitions.values():
            all_packages.extend(category.keys())
        return self.install_packages(all_packages)

    def get_installation_report(self) -> str:
        """Generate installation report."""
        report_lines = [
            "=" * 60,
            "CROSS-PLATFORM PACKAGE INSTALLATION REPORT",
            "=" * 60,
            "",
            f"Installation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Platform: {self.platform}",
            f"Available Package Managers: {[pm.name for pm in self.package_managers]}",
            "",
            "Installation Statistics:",
            f"  Total Packages: {self.installation_stats['total_packages']}",
            f"  Successful Installations: {self.installation_stats['successful_installations']}",
            f"  Failed Installations: {self.installation_stats['failed_installations']}",
            f"  Already Installed: {self.installation_stats['already_installed']}",
            f"  Total Installation Time: {self.installation_stats['total_time']:.2f} seconds",
            "",
            f"Success Rate: {(self.installation_stats['successful_installations'] / max(1, self.installation_stats['total_packages'])) * 100:.1f}%",
            "",
            "=" * 60,
        ]

        return "\n".join(report_lines)

    def validate_dependencies(self) -> Dict[str, bool]:
        """Validate that all dependencies are correctly installed."""
        validation_results = {}

        # Test imports for Python packages
        python_packages = {
            "matplotlib": "matplotlib.pyplot",
            "numpy": "numpy",
            "seaborn": "seaborn",
            "plotly": "plotly.graph_objects",
            "bokeh": "bokeh.plotting",
            "dash": "dash",
            "scipy": "scipy",
            "pandas": "pandas",
            "scikit-learn": "sklearn",
            "networkx": "networkx",
            "igraph": "igraph",
        }

        for package_name, import_name in python_packages.items():
            try:
                __import__(import_name)
                validation_results[package_name] = True
                self.logger.debug(f"✓ Successfully imported {import_name}")
            except ImportError:
                validation_results[package_name] = False
                self.logger.warning(f"✗ Failed to import {import_name}")

        return validation_results


def main():
    """Main entry point for package installation script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Cross-Platform Package Installation Automation"
    )

    parser.add_argument(
        "--packages", nargs="+", help="Specific packages to install"
    )

    parser.add_argument(
        "--category",
        choices=["visualization", "scientific", "network", "all"],
        help="Category of packages to install",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate installations after completion",
    )

    parser.add_argument(
        "--sequential",
        action="store_true",
        help="Install packages sequentially (not in parallel)",
    )

    args = parser.parse_args()

    # Create installer
    installer = CrossPlatformPackageInstaller(verbose=args.verbose)

    # Determine what to install
    results = []

    if args.packages:
        results = installer.install_packages(
            args.packages, parallel=not args.sequential
        )
    elif args.category:
        if args.category == "visualization":
            results = installer.install_visualization_packages()
        elif args.category == "scientific":
            results = installer.install_scientific_packages()
        elif args.category == "network":
            results = installer.install_network_packages()
        elif args.category == "all":
            results = installer.install_all_packages()
    else:
        print("Please specify either --packages or --category")
        sys.exit(1)

    # Print results
    print("\nInstallation Results:")
    print("-" * 50)
    for result in results:
        status = "✓" if result.success else "✗"
        print(f"{status} {result.package}: {result.message}")

    # Generate report
    report = installer.get_installation_report()
    print(f"\n{report}")

    # Save report
    report_file = f"package_installation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, "w") as f:
        f.write(report)
    print(f"\nDetailed report saved to: {report_file}")

    # Validate if requested
    if args.validate:
        print("\nValidating installations...")
        validation_results = installer.validate_dependencies()

        print("\nValidation Results:")
        print("-" * 30)
        for package, valid in validation_results.items():
            status = "✓" if valid else "✗"
            print(f"{status} {package}")

    # Exit with appropriate code
    failed_count = sum(1 for result in results if not result.success)
    sys.exit(0 if failed_count == 0 else 1)


if __name__ == "__main__":
    main()
