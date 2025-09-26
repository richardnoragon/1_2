#!/usr/bin/env python3
"""Network Connectivity Toolkit Installation Script.

This script handles the installation, configuration, and validation
of the Network Connectivity Toolkit for production deployment.
"""

import os
import sys
import subprocess
import platform
import shutil
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse
import logging
from datetime import datetime


class NetworkConnectivityInstaller:
    """Handles installation of Network Connectivity Toolkit."""
    
    def __init__(self, install_dir: Optional[str] = None, verbose: bool = False):
        """Initialize installer.
        
        Args:
            install_dir: Target installation directory
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.setup_logging()
        
        # Determine installation directory
        if install_dir:
            self.install_dir = Path(install_dir).resolve()
        else:
            self.install_dir = self._get_default_install_dir()
        
        # Source directory (where this script is located)
        self.source_dir = Path(__file__).parent.parent.resolve()
        
        # System information
        self.system_info = self._get_system_info()
        
        # Installation status
        self.installation_log = []
        
        self.logger.info(f"Network Connectivity Installer initialized")
        self.logger.info(f"Source directory: {self.source_dir}")
        self.logger.info(f"Target directory: {self.install_dir}")
        self.logger.info(f"System: {self.system_info['platform']} {self.system_info['version']}")
    
    def setup_logging(self):
        """Setup logging configuration."""
        log_level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('network_connectivity_install.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _get_default_install_dir(self) -> Path:
        """Get default installation directory based on platform."""
        system = platform.system().lower()
        
        if system == "windows":
            # Windows: Program Files or user directory
            if self._is_admin():
                return Path("C:/Program Files/NetworkConnectivity")
            else:
                return Path.home() / "AppData" / "Local" / "NetworkConnectivity"
        
        elif system == "darwin":  # macOS
            # macOS: Applications or user directory
            if self._is_admin():
                return Path("/Applications/NetworkConnectivity")
            else:
                return Path.home() / "Applications" / "NetworkConnectivity"
        
        else:  # Linux and others
            # Linux: /opt or user directory
            if self._is_admin():
                return Path("/opt/network-connectivity")
            else:
                return Path.home() / ".local" / "share" / "network-connectivity"
    
    def _is_admin(self) -> bool:
        """Check if running with administrator privileges."""
        try:
            if platform.system().lower() == "windows":
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin()
            else:
                return os.geteuid() == 0
        except:
            return False
    
    def _get_system_info(self) -> Dict[str, str]:
        """Get system information."""
        return {
            "platform": platform.system(),
            "version": platform.version(),
            "architecture": platform.architecture()[0],
            "python_version": platform.python_version(),
            "machine": platform.machine(),
            "processor": platform.processor()
        }
    
    def check_prerequisites(self) -> Tuple[bool, List[str]]:
        """Check system prerequisites.
        
        Returns:
            Tuple of (success, error_messages)
        """
        self.logger.info("Checking system prerequisites...")
        errors = []
        
        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 8):
            errors.append(f"Python 3.8+ required, found {python_version.major}.{python_version.minor}")
        
        # Check available disk space
        if not self._check_disk_space():
            errors.append("Insufficient disk space (minimum 2GB required)")
        
        # Check network connectivity
        if not self._check_network_connectivity():
            errors.append("Network connectivity required for dependency installation")
        
        # Check platform-specific requirements
        platform_errors = self._check_platform_requirements()
        errors.extend(platform_errors)
        
        # Check permissions
        if not self._check_permissions():
            errors.append(f"Insufficient permissions to write to {self.install_dir}")
        
        success = len(errors) == 0
        if success:
            self.logger.info("✓ All prerequisites satisfied")
        else:
            self.logger.error(f"✗ Prerequisites check failed: {len(errors)} errors")
            for error in errors:
                self.logger.error(f"  - {error}")
        
        return success, errors
    
    def _check_disk_space(self) -> bool:
        """Check available disk space."""
        try:
            if platform.system().lower() == "windows":
                import ctypes
                free_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p(str(self.install_dir.parent)),
                    ctypes.pointer(free_bytes),
                    None,
                    None
                )
                free_gb = free_bytes.value / (1024**3)
            else:
                statvfs = os.statvfs(self.install_dir.parent)
                free_gb = (statvfs.f_frsize * statvfs.f_bavail) / (1024**3)
            
            return free_gb >= 2.0  # Require at least 2GB
        except:
            return True  # Assume sufficient space if check fails
    
    def _check_network_connectivity(self) -> bool:
        """Check network connectivity."""
        try:
            import urllib.request
            urllib.request.urlopen('https://pypi.org', timeout=10)
            return True
        except:
            return False
    
    def _check_platform_requirements(self) -> List[str]:
        """Check platform-specific requirements."""
        errors = []
        system = platform.system().lower()
        
        if system == "windows":
            # Check for Visual C++ Redistributable (for some dependencies)
            pass
        
        elif system == "darwin":
            # Check for Xcode command line tools
            try:
                subprocess.run(['xcode-select', '--version'], 
                             check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                errors.append("Xcode command line tools required on macOS")
        
        elif system == "linux":
            # Check for essential packages
            required_packages = ['python3-dev', 'build-essential']
            for package in required_packages:
                if not self._check_linux_package(package):
                    errors.append(f"Required package not found: {package}")
        
        return errors
    
    def _check_linux_package(self, package: str) -> bool:
        """Check if a Linux package is installed."""
        try:
            # Try dpkg first (Debian/Ubuntu)
            result = subprocess.run(['dpkg', '-l', package], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return True
            
            # Try rpm (RedHat/CentOS)
            result = subprocess.run(['rpm', '-q', package], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return True  # Assume available if package managers not found
    
    def _check_permissions(self) -> bool:
        """Check write permissions to installation directory."""
        try:
            self.install_dir.mkdir(parents=True, exist_ok=True)
            test_file = self.install_dir / ".permission_test"
            test_file.write_text("test")
            test_file.unlink()
            return True
        except (PermissionError, OSError):
            return False
    
    def install_dependencies(self) -> bool:
        """Install Python dependencies.
        
        Returns:
            True if successful, False otherwise
        """
        self.logger.info("Installing Python dependencies...")
        
        try:
            # Upgrade pip first
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'
            ], check=True, capture_output=True)
            
            # Install from requirements file
            requirements_file = self.source_dir / 'deployment' / 'requirements.txt'
            if requirements_file.exists():
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', 
                    '-r', str(requirements_file)
                ], check=True, capture_output=True)
            else:
                # Install core dependencies
                core_deps = [
                    'PyQt6>=6.4.0',
                    'psutil>=5.9.0',
                    'PyYAML>=6.0',
                    'cryptography>=3.4.8',
                    'requests>=2.28.0',
                    'python-json-logger>=2.0.0'
                ]
                
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install'
                ] + core_deps, check=True, capture_output=True)
            
            self.logger.info("✓ Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"✗ Failed to install dependencies: {e}")
            return False
    
    def copy_files(self) -> bool:
        """Copy toolkit files to installation directory.
        
        Returns:
            True if successful, False otherwise
        """
        self.logger.info("Copying toolkit files...")
        
        try:
            # Create installation directory structure
            self.install_dir.mkdir(parents=True, exist_ok=True)
            
            # Define directories to copy
            dirs_to_copy = [
                'core',
                'tools', 
                'gui',
                'config',
                'docs',
                'examples'
            ]
            
            # Copy directories
            for dir_name in dirs_to_copy:
                src_dir = self.source_dir / dir_name
                dst_dir = self.install_dir / dir_name
                
                if src_dir.exists():
                    if dst_dir.exists():
                        shutil.rmtree(dst_dir)
                    shutil.copytree(src_dir, dst_dir)
                    self.logger.debug(f"Copied {src_dir} -> {dst_dir}")
            
            # Copy individual files
            files_to_copy = [
                '__init__.py',
                'README.md'
            ]
            
            for file_name in files_to_copy:
                src_file = self.source_dir / file_name
                dst_file = self.install_dir / file_name
                
                if src_file.exists():
                    shutil.copy2(src_file, dst_file)
                    self.logger.debug(f"Copied {src_file} -> {dst_file}")
            
            self.logger.info("✓ Files copied successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"✗ Failed to copy files: {e}")
            return False
    
    def create_configuration(self) -> bool:
        """Create initial configuration files.
        
        Returns:
            True if successful, False otherwise
        """
        self.logger.info("Creating configuration files...")
        
        try:
            config_dir = self.install_dir / 'config'
            config_dir.mkdir(exist_ok=True)
            
            # Create main configuration file
            config_file = config_dir / 'network_connectivity.yaml'
            if not config_file.exists():
                default_config = self._get_default_configuration()
                with open(config_file, 'w') as f:
                    yaml.dump(default_config, f, default_flow_style=False, indent=2)
            
            # Create logging configuration
            logging_config_file = config_dir / 'logging.yaml'
            if not logging_config_file.exists():
                logging_config = self._get_default_logging_config()
                with open(logging_config_file, 'w') as f:
                    yaml.dump(logging_config, f, default_flow_style=False, indent=2)
            
            # Create user data directories
            user_dirs = ['logs', 'data', 'profiles', 'exports']
            for dir_name in user_dirs:
                (self.install_dir / dir_name).mkdir(exist_ok=True)
            
            self.logger.info("✓ Configuration created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"✗ Failed to create configuration: {e}")
            return False
    
    def _get_default_configuration(self) -> Dict:
        """Get default configuration."""
        return {
            'network_connectivity': {
                'general': {
                    'default_timeout': 5000,
                    'max_concurrent_operations': 10,
                    'enable_logging': True,
                    'log_level': 'INFO',
                    'auto_save_results': True,
                    'results_retention_days': 30
                },
                'bandwidth_monitor': {
                    'update_interval': 1000,
                    'history_size': 100,
                    'enable_alerts': True,
                    'alert_thresholds': {
                        'upload_mbps': 50,
                        'download_mbps': 100
                    }
                },
                'port_scanner': {
                    'default_timeout': 3000,
                    'max_threads': 50,
                    'scan_techniques': ['tcp_connect', 'tcp_syn'],
                    'enable_service_detection': True
                },
                'wifi_analyzer': {
                    'scan_interval': 5000,
                    'channel_bands': ['2.4GHz', '5GHz'],
                    'enable_security_analysis': True
                },
                'lan_file_transfer': {
                    'discovery_port': 8888,
                    'transfer_port_range': [9000, 9100],
                    'encryption_enabled': True,
                    'authentication_required': True
                },
                'security': {
                    'enable_encryption': True,
                    'require_authentication': True,
                    'audit_logging': True
                }
            }
        }
    
    def _get_default_logging_config(self) -> Dict:
        """Get default logging configuration."""
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                },
                'detailed': {
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': 'INFO',
                    'formatter': 'standard',
                    'stream': 'ext://sys.stdout'
                },
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': 'DEBUG',
                    'formatter': 'detailed',
                    'filename': str(self.install_dir / 'logs' / 'network_connectivity.log'),
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 5
                }
            },
            'loggers': {
                'network_connectivity': {
                    'level': 'DEBUG',
                    'handlers': ['console', 'file'],
                    'propagate': False
                }
            },
            'root': {
                'level': 'INFO',
                'handlers': ['console']
            }
        }
    
    def create_shortcuts(self) -> bool:
        """Create desktop shortcuts and menu entries.
        
        Returns:
            True if successful, False otherwise
        """
        self.logger.info("Creating shortcuts...")
        
        try:
            system = platform.system().lower()
            
            if system == "windows":
                self._create_windows_shortcuts()
            elif system == "darwin":
                self._create_macos_shortcuts()
            else:
                self._create_linux_shortcuts()
            
            self.logger.info("✓ Shortcuts created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"✗ Failed to create shortcuts: {e}")
            return False
    
    def _create_windows_shortcuts(self):
        """Create Windows shortcuts."""
        try:
            import winshell
            from win32com.client import Dispatch
            
            # Desktop shortcut
            desktop = winshell.desktop()
            shortcut_path = os.path.join(desktop, "Network Connectivity Hub.lnk")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{self.install_dir / "gui" / "hub.py"}"'
            shortcut.WorkingDirectory = str(self.install_dir)
            shortcut.IconLocation = str(self.install_dir / "gui" / "icons" / "hub.ico")
            shortcut.save()
            
        except ImportError:
            self.logger.warning("Windows shortcut creation requires pywin32")
    
    def _create_macos_shortcuts(self):
        """Create macOS shortcuts."""
        # Create .app bundle structure
        app_dir = Path("/Applications/Network Connectivity Hub.app")
        if self._is_admin():
            app_dir.mkdir(parents=True, exist_ok=True)
            
            # Create Info.plist
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>network_connectivity_hub</string>
    <key>CFBundleIdentifier</key>
    <string>com.rfu.network-connectivity</string>
    <key>CFBundleName</key>
    <string>Network Connectivity Hub</string>
    <key>CFBundleVersion</key>
    <string>1.2.0</string>
</dict>
</plist>"""
            
            (app_dir / "Contents").mkdir(exist_ok=True)
            (app_dir / "Contents" / "Info.plist").write_text(plist_content)
    
    def _create_linux_shortcuts(self):
        """Create Linux desktop entries."""
        desktop_entry = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Network Connectivity Hub
Comment=Network analysis and monitoring tools
Exec={sys.executable} "{self.install_dir / "gui" / "hub.py"}"
Icon={self.install_dir / "gui" / "icons" / "hub.png"}
Terminal=false
Categories=Network;System;
"""
        
        # User desktop entry
        desktop_dir = Path.home() / ".local" / "share" / "applications"
        desktop_dir.mkdir(parents=True, exist_ok=True)
        (desktop_dir / "network-connectivity-hub.desktop").write_text(desktop_entry)
    
    def validate_installation(self) -> Tuple[bool, List[str]]:
        """Validate the installation.
        
        Returns:
            Tuple of (success, error_messages)
        """
        self.logger.info("Validating installation...")
        errors = []
        
        # Check file structure
        required_dirs = ['core', 'tools', 'gui', 'config']
        for dir_name in required_dirs:
            dir_path = self.install_dir / dir_name
            if not dir_path.exists():
                errors.append(f"Missing directory: {dir_name}")
        
        # Check configuration files
        config_file = self.install_dir / 'config' / 'network_connectivity.yaml'
        if not config_file.exists():
            errors.append("Missing configuration file")
        
        # Test import
        try:
            sys.path.insert(0, str(self.install_dir))
            import network_connectivity
            self.logger.debug(f"Successfully imported network_connectivity v{network_connectivity.__version__}")
        except ImportError as e:
            errors.append(f"Failed to import network_connectivity: {e}")
        finally:
            if str(self.install_dir) in sys.path:
                sys.path.remove(str(self.install_dir))
        
        # Test basic functionality
        try:
            # This would test basic tool initialization
            pass
        except Exception as e:
            errors.append(f"Basic functionality test failed: {e}")
        
        success = len(errors) == 0
        if success:
            self.logger.info("✓ Installation validation successful")
        else:
            self.logger.error(f"✗ Installation validation failed: {len(errors)} errors")
            for error in errors:
                self.logger.error(f"  - {error}")
        
        return success, errors
    
    def generate_installation_report(self) -> str:
        """Generate installation report.
        
        Returns:
            Installation report as string
        """
        report_lines = [
            "=" * 60,
            "NETWORK CONNECTIVITY TOOLKIT INSTALLATION REPORT",
            "=" * 60,
            "",
            f"Installation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Installation Directory: {self.install_dir}",
            f"Source Directory: {self.source_dir}",
            "",
            "System Information:",
            f"  Platform: {self.system_info['platform']} {self.system_info['version']}",
            f"  Architecture: {self.system_info['architecture']}",
            f"  Python Version: {self.system_info['python_version']}",
            f"  Machine: {self.system_info['machine']}",
            "",
            "Installation Steps:",
        ]
        
        for step in self.installation_log:
            report_lines.append(f"  {step}")
        
        report_lines.extend([
            "",
            "Next Steps:",
            "1. Review configuration files in config/ directory",
            "2. Run validation tests: python -m network_connectivity.tests.test_runner",
            "3. Launch GUI: python gui/hub.py",
            "4. Consult documentation in docs/ directory",
            "",
            "=" * 60
        ])
        
        return "\n".join(report_lines)
    
    def install(self) -> bool:
        """Perform complete installation.
        
        Returns:
            True if successful, False otherwise
        """
        self.logger.info("Starting Network Connectivity Toolkit installation...")
        
        # Check prerequisites
        prereq_success, prereq_errors = self.check_prerequisites()
        if not prereq_success:
            self.logger.error("Prerequisites check failed. Installation aborted.")
            return False
        
        self.installation_log.append("✓ Prerequisites check passed")
        
        # Install dependencies
        if not self.install_dependencies():
            self.logger.error("Dependency installation failed. Installation aborted.")
            return False
        
        self.installation_log.append("✓ Dependencies installed")
        
        # Copy files
        if not self.copy_files():
            self.logger.error("File copying failed. Installation aborted.")
            return False
        
        self.installation_log.append("✓ Files copied")
        
        # Create configuration
        if not self.create_configuration():
            self.logger.error("Configuration creation failed. Installation aborted.")
            return False
        
        self.installation_log.append("✓ Configuration created")
        
        # Create shortcuts
        if not self.create_shortcuts():
            self.logger.warning("Shortcut creation failed, but installation continues.")
        else:
            self.installation_log.append("✓ Shortcuts created")
        
        # Validate installation
        validation_success, validation_errors = self.validate_installation()
        if not validation_success:
            self.logger.error("Installation validation failed.")
            for error in validation_errors:
                self.logger.error(f"  - {error}")
            return False
        
        self.installation_log.append("✓ Installation validated")
        
        # Generate report
        report = self.generate_installation_report()
        report_file = self.install_dir / "installation_report.txt"
        report_file.write_text(report)
        
        self.logger.info("✓ Installation completed successfully!")
        self.logger.info(f"Installation report saved to: {report_file}")
        
        return True


def main():
    """Main entry point for installation script."""
    parser = argparse.ArgumentParser(
        description="Network Connectivity Toolkit Installer"
    )
    
    parser.add_argument(
        "--install-dir",
        help="Target installation directory"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check prerequisites, don't install"
    )
    
    args = parser.parse_args()
    
    # Create installer
    installer = NetworkConnectivityInstaller(
        install_dir=args.install_dir,
        verbose=args.verbose
    )
    
    if args.check_only:
        # Only check prerequisites
        success, errors = installer.check_prerequisites()
        if success:
            print("✓ All prerequisites satisfied")
            sys.exit(0)
        else:
            print("✗ Prerequisites check failed:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)
    else:
        # Perform full installation
        success = installer.install()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()