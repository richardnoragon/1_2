#!/usr/bin/env python3
"""Test suite for CrossPlatformPackageInstaller.

This module provides comprehensive tests for the package installation
automation system across Windows, Linux, and macOS platforms.
"""

import json
import os
import platform
import subprocess
import sys
import tempfile
import time
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, Mock, call, patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from cross_platform.package_installer import (AptPackageManager,
                                              CrossPlatformPackageInstaller,
                                              HomebrewPackageManager,
                                              PackageInfo,
                                              PackageInstallationResult,
                                              PipPackageManager,
                                              YumDnfPackageManager)


class TestPackageInfo(unittest.TestCase):
    """Test cases for PackageInfo dataclass."""
    
    def test_package_info_creation(self):
        """Test PackageInfo creation with all fields."""
        package = PackageInfo(
            name="pytest",
            version="7.4.0",
            installed=True,
            location="/usr/local/lib/python3.11/site-packages",
            dependencies=["packaging", "pluggy"]
        )
        
        self.assertEqual(package.name, "pytest")
        self.assertEqual(package.version, "7.4.0")
        self.assertTrue(package.installed)
        self.assertEqual(package.location, "/usr/local/lib/python3.11/site-packages")
        self.assertEqual(len(package.dependencies), 2)
    
    def test_package_info_defaults(self):
        """Test PackageInfo creation with default values."""
        package = PackageInfo(name="numpy")
        
        self.assertEqual(package.name, "numpy")
        self.assertIsNone(package.version)
        self.assertFalse(package.installed)
        self.assertIsNone(package.location)
        self.assertEqual(package.dependencies, [])


class TestPackageInstallationResult(unittest.TestCase):
    """Test cases for PackageInstallationResult dataclass."""
    
    def test_installation_result_success(self):
        """Test successful installation result."""
        result = PackageInstallationResult(
            package_name="requests",
            success=True,
            version_installed="2.31.0",
            install_time=2.5,
            output="Successfully installed requests-2.31.0"
        )
        
        self.assertEqual(result.package_name, "requests")
        self.assertTrue(result.success)
        self.assertEqual(result.version_installed, "2.31.0")
        self.assertEqual(result.install_time, 2.5)
        self.assertEqual(len(result.errors), 0)
    
    def test_installation_result_failure(self):
        """Test failed installation result."""
        result = PackageInstallationResult(
            package_name="nonexistent-package",
            success=False,
            errors=["Package not found", "Installation failed"]
        )
        
        self.assertEqual(result.package_name, "nonexistent-package")
        self.assertFalse(result.success)
        self.assertIsNone(result.version_installed)
        self.assertEqual(len(result.errors), 2)


class TestPipPackageManager(unittest.TestCase):
    """Test cases for PipPackageManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = PipPackageManager()
    
    @patch('subprocess.run')
    def test_check_availability_success(self, mock_run):
        """Test successful pip availability check."""
        mock_run.return_value = Mock(returncode=0, stdout="pip 23.1.2")
        
        available = self.manager.check_availability()
        
        self.assertTrue(available)
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_check_availability_failure(self, mock_run):
        """Test failed pip availability check."""
        mock_run.side_effect = FileNotFoundError("pip not found")
        
        available = self.manager.check_availability()
        
        self.assertFalse(available)
    
    @patch('subprocess.run')
    def test_install_package_success(self, mock_run):
        """Test successful package installation."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Successfully installed requests-2.31.0",
            stderr=""
        )
        
        result = self.manager.install_package("requests")
        
        self.assertTrue(result.success)
        self.assertEqual(result.package_name, "requests")
        self.assertIn("Successfully installed", result.output)
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_install_package_failure(self, mock_run):
        """Test failed package installation."""
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="ERROR: Could not find a version that satisfies the requirement"
        )
        
        result = self.manager.install_package("nonexistent-package")
        
        self.assertFalse(result.success)
        self.assertEqual(result.package_name, "nonexistent-package")
        self.assertGreater(len(result.errors), 0)
    
    @patch('subprocess.run')
    def test_install_package_with_version(self, mock_run):
        """Test package installation with specific version."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Successfully installed requests-2.30.0",
            stderr=""
        )
        
        result = self.manager.install_package("requests", version="2.30.0")
        
        self.assertTrue(result.success)
        # Verify that version was included in the command
        args = mock_run.call_args[0][0]
        self.assertIn("requests==2.30.0", args)
    
    @patch('subprocess.run')
    def test_uninstall_package_success(self, mock_run):
        """Test successful package uninstallation."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Successfully uninstalled requests-2.31.0",
            stderr=""
        )
        
        result = self.manager.uninstall_package("requests")
        
        self.assertTrue(result.success)
        self.assertEqual(result.package_name, "requests")
        self.assertIn("Successfully uninstalled", result.output)
    
    @patch('subprocess.run')
    def test_list_installed_packages(self, mock_run):
        """Test listing installed packages."""
        mock_output = """requests==2.31.0
numpy==1.24.3
pandas==2.0.2"""
        
        mock_run.return_value = Mock(
            returncode=0,
            stdout=mock_output,
            stderr=""
        )
        
        packages = self.manager.list_installed_packages()
        
        self.assertEqual(len(packages), 3)
        self.assertEqual(packages[0].name, "requests")
        self.assertEqual(packages[0].version, "2.31.0")
        self.assertTrue(packages[0].installed)
    
    @patch('subprocess.run')
    def test_get_package_info_installed(self, mock_run):
        """Test getting info for installed package."""
        mock_output = """Name: requests
Version: 2.31.0
Location: /usr/local/lib/python3.11/site-packages
Requires: charset-normalizer, idna, urllib3, certifi"""
        
        mock_run.return_value = Mock(
            returncode=0,
            stdout=mock_output,
            stderr=""
        )
        
        package_info = self.manager.get_package_info("requests")
        
        self.assertEqual(package_info.name, "requests")
        self.assertEqual(package_info.version, "2.31.0")
        self.assertTrue(package_info.installed)
        self.assertIn("/usr/local/lib/python3.11/site-packages", package_info.location)
        self.assertGreater(len(package_info.dependencies), 0)
    
    @patch('subprocess.run')
    def test_get_package_info_not_installed(self, mock_run):
        """Test getting info for non-installed package."""
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="WARNING: Package(s) not found: nonexistent-package"
        )
        
        package_info = self.manager.get_package_info("nonexistent-package")
        
        self.assertEqual(package_info.name, "nonexistent-package")
        self.assertIsNone(package_info.version)
        self.assertFalse(package_info.installed)


class TestAptPackageManager(unittest.TestCase):
    """Test cases for AptPackageManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = AptPackageManager()
    
    @patch('subprocess.run')
    def test_check_availability_success(self, mock_run):
        """Test successful apt availability check."""
        mock_run.return_value = Mock(returncode=0, stdout="apt 2.4.9")
        
        available = self.manager.check_availability()
        
        self.assertTrue(available)
    
    @patch('subprocess.run')
    def test_install_package_success(self, mock_run):
        """Test successful package installation with apt."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Reading package lists...\nThe following NEW packages will be installed:\n  curl",
            stderr=""
        )
        
        result = self.manager.install_package("curl")
        
        self.assertTrue(result.success)
        self.assertEqual(result.package_name, "curl")
        # Check that sudo was used
        args = mock_run.call_args[0][0]
        self.assertIn("sudo", args)
        self.assertIn("apt-get", args)
        self.assertIn("install", args)
    
    @patch('subprocess.run')
    def test_update_package_lists(self, mock_run):
        """Test package list update."""
        mock_run.return_value = Mock(returncode=0)
        
        success = self.manager.update_package_lists()
        
        self.assertTrue(success)
        args = mock_run.call_args[0][0]
        self.assertIn("apt-get", args)
        self.assertIn("update", args)


class TestYumDnfPackageManager(unittest.TestCase):
    """Test cases for YumDnfPackageManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = YumDnfPackageManager()
    
    @patch('subprocess.run')
    def test_check_availability_dnf_success(self, mock_run):
        """Test successful dnf availability check."""
        mock_run.side_effect = [
            Mock(returncode=0, stdout="dnf 4.14.0"),  # dnf check
            Mock(returncode=1)  # yum check (should fail)
        ]
        
        available = self.manager.check_availability()
        
        self.assertTrue(available)
        self.assertEqual(self.manager.command, "dnf")
    
    @patch('subprocess.run')
    def test_check_availability_yum_fallback(self, mock_run):
        """Test fallback to yum when dnf unavailable."""
        mock_run.side_effect = [
            Mock(returncode=1),  # dnf check fails
            Mock(returncode=0, stdout="yum 3.4.3")  # yum check succeeds
        ]
        
        available = self.manager.check_availability()
        
        self.assertTrue(available)
        self.assertEqual(self.manager.command, "yum")
    
    @patch('subprocess.run')
    def test_install_package_success(self, mock_run):
        """Test successful package installation with dnf/yum."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Installing dependencies:\nInstalled:\n  curl.x86_64",
            stderr=""
        )
        
        result = self.manager.install_package("curl")
        
        self.assertTrue(result.success)
        self.assertEqual(result.package_name, "curl")


class TestHomebrewPackageManager(unittest.TestCase):
    """Test cases for HomebrewPackageManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = HomebrewPackageManager()
    
    @patch('subprocess.run')
    def test_check_availability_success(self, mock_run):
        """Test successful brew availability check."""
        mock_run.return_value = Mock(returncode=0, stdout="Homebrew 4.0.21")
        
        available = self.manager.check_availability()
        
        self.assertTrue(available)
    
    @patch('subprocess.run')
    def test_install_package_success(self, mock_run):
        """Test successful package installation with brew."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="==> Downloading https://...\n==> Installing curl",
            stderr=""
        )
        
        result = self.manager.install_package("curl")
        
        self.assertTrue(result.success)
        self.assertEqual(result.package_name, "curl")
        
        args = mock_run.call_args[0][0]
        self.assertIn("brew", args)
        self.assertIn("install", args)
    
    @patch('subprocess.run')
    def test_update_package_lists(self, mock_run):
        """Test package list update (brew update)."""
        mock_run.return_value = Mock(returncode=0)
        
        success = self.manager.update_package_lists()
        
        self.assertTrue(success)
        args = mock_run.call_args[0][0]
        self.assertIn("brew", args)
        self.assertIn("update", args)


class TestCrossPlatformPackageInstaller(unittest.TestCase):
    """Test cases for CrossPlatformPackageInstaller."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.installer = CrossPlatformPackageInstaller(verbose=False)
    
    @patch('platform.system')
    def test_detect_platform_windows(self, mock_system):
        """Test Windows platform detection."""
        mock_system.return_value = "Windows"
        
        installer = CrossPlatformPackageInstaller()
        
        self.assertEqual(installer.platform, "windows")
        self.assertIsInstance(installer.primary_manager, PipPackageManager)
    
    @patch('platform.system')
    def test_detect_platform_linux(self, mock_system):
        """Test Linux platform detection."""
        mock_system.return_value = "Linux"
        
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.side_effect = lambda path: str(path).endswith('apt')
            
            installer = CrossPlatformPackageInstaller()
            
            self.assertEqual(installer.platform, "linux")
            # Should detect apt as available system manager
            system_managers = [type(mgr).__name__ for mgr in installer.system_managers]
            self.assertIn("AptPackageManager", system_managers)
    
    @patch('platform.system')
    def test_detect_platform_macos(self, mock_system):
        """Test macOS platform detection."""
        mock_system.return_value = "Darwin"
        
        installer = CrossPlatformPackageInstaller()
        
        self.assertEqual(installer.platform, "darwin")
    
    def test_validate_package_name_valid(self):
        """Test validation of valid package names."""
        valid_names = [
            "requests",
            "numpy",
            "scikit-learn",
            "python-dateutil",
            "PyQt5",
            "requests[security]"
        ]
        
        for name in valid_names:
            with self.subTest(name=name):
                result = self.installer._validate_package_name(name)
                self.assertTrue(result)
    
    def test_validate_package_name_invalid(self):
        """Test validation of invalid package names."""
        invalid_names = [
            "",
            "  ",
            "package with spaces",
            "package/with/slashes",
            "package;with;semicolons",
            "package&&with&&ampersands"
        ]
        
        for name in invalid_names:
            with self.subTest(name=name):
                result = self.installer._validate_package_name(name)
                self.assertFalse(result)
    
    def test_parse_requirements_file(self):
        """Test parsing of requirements file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("requests==2.31.0\n")
            f.write("numpy>=1.20.0\n")
            f.write("# This is a comment\n")
            f.write("pandas  # Another comment\n")
            f.write("\n")  # Empty line
            f.write("matplotlib[web]\n")
            temp_file = f.name
        
        try:
            packages = self.installer._parse_requirements_file(temp_file)
            
            expected_packages = [
                "requests==2.31.0",
                "numpy>=1.20.0",
                "pandas",
                "matplotlib[web]"
            ]
            
            self.assertEqual(packages, expected_packages)
        
        finally:
            os.unlink(temp_file)
    
    def test_parse_requirements_file_not_found(self):
        """Test parsing of non-existent requirements file."""
        packages = self.installer._parse_requirements_file("nonexistent.txt")
        self.assertEqual(packages, [])
    
    @patch.object(CrossPlatformPackageInstaller, '_install_single_package')
    def test_install_packages_sequential(self, mock_install):
        """Test sequential package installation."""
        # Mock successful installations
        mock_install.side_effect = [
            PackageInstallationResult("requests", True, "2.31.0", 1.0),
            PackageInstallationResult("numpy", True, "1.24.3", 2.0)
        ]
        
        packages = ["requests", "numpy"]
        results = self.installer.install_packages(packages, parallel=False)
        
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r.success for r in results))
        self.assertEqual(mock_install.call_count, 2)
    
    @patch.object(CrossPlatformPackageInstaller, '_install_single_package')
    def test_install_packages_parallel(self, mock_install):
        """Test parallel package installation."""
        # Mock successful installations
        mock_install.side_effect = [
            PackageInstallationResult("requests", True, "2.31.0", 1.0),
            PackageInstallationResult("numpy", True, "1.24.3", 2.0),
            PackageInstallationResult("pandas", True, "2.0.2", 3.0)
        ]
        
        packages = ["requests", "numpy", "pandas"]
        results = self.installer.install_packages(packages, parallel=True, max_workers=2)
        
        self.assertEqual(len(results), 3)
        self.assertTrue(all(r.success for r in results))
        self.assertEqual(mock_install.call_count, 3)
    
    @patch.object(PipPackageManager, 'install_package')
    def test_install_single_package_success(self, mock_pip_install):
        """Test successful single package installation."""
        mock_pip_install.return_value = PackageInstallationResult(
            "requests", True, "2.31.0", 1.5
        )
        
        result = self.installer._install_single_package("requests")
        
        self.assertTrue(result.success)
        self.assertEqual(result.package_name, "requests")
        self.assertEqual(result.version_installed, "2.31.0")
        mock_pip_install.assert_called_once_with("requests", version=None)
    
    @patch.object(PipPackageManager, 'install_package')
    def test_install_single_package_failure(self, mock_pip_install):
        """Test failed single package installation."""
        mock_pip_install.return_value = PackageInstallationResult(
            "nonexistent", False, None, 0.5, 
            errors=["Package not found"]
        )
        
        result = self.installer._install_single_package("nonexistent")
        
        self.assertFalse(result.success)
        self.assertEqual(result.package_name, "nonexistent")
        self.assertIsNone(result.version_installed)
        self.assertGreater(len(result.errors), 0)
    
    def test_generate_installation_report(self):
        """Test installation report generation."""
        results = [
            PackageInstallationResult("requests", True, "2.31.0", 1.0),
            PackageInstallationResult("numpy", True, "1.24.3", 2.0),
            PackageInstallationResult("nonexistent", False, None, 0.5, 
                                   errors=["Package not found"])
        ]
        
        report = self.installer.generate_installation_report(results)
        
        self.assertIn("PACKAGE INSTALLATION REPORT", report)
        self.assertIn("Total packages: 3", report)
        self.assertIn("Successful: 2", report)
        self.assertIn("Failed: 1", report)
        self.assertIn("requests", report)
        self.assertIn("numpy", report)
        self.assertIn("nonexistent", report)
    
    def test_export_installation_results_json(self):
        """Test exporting installation results to JSON."""
        results = [
            PackageInstallationResult("requests", True, "2.31.0", 1.0),
            PackageInstallationResult("numpy", False, None, 0.5, 
                                   errors=["Installation failed"])
        ]
        
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = self.installer.export_installation_results(
                results, export_format="json", output_dir=temp_dir
            )
            
            self.assertTrue(os.path.exists(filename))
            self.assertTrue(filename.endswith('.json'))
            
            # Verify JSON content
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.assertIn("installation_date", data)
            self.assertIn("platform", data)
            self.assertEqual(len(data["results"]), 2)
    
    @patch('builtins.input', return_value='y')
    def test_confirm_installation_yes(self, mock_input):
        """Test installation confirmation with yes."""
        packages = ["requests", "numpy"]
        
        result = self.installer._confirm_installation(packages)
        
        self.assertTrue(result)
        mock_input.assert_called_once()
    
    @patch('builtins.input', return_value='n')
    def test_confirm_installation_no(self, mock_input):
        """Test installation confirmation with no."""
        packages = ["requests", "numpy"]
        
        result = self.installer._confirm_installation(packages)
        
        self.assertFalse(result)


class TestCrossPlatformPackageInstallerIntegration(unittest.TestCase):
    """Integration tests for CrossPlatformPackageInstaller."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.installer = CrossPlatformPackageInstaller(verbose=True)
    
    @unittest.skipUnless(
        sys.platform.startswith('win') or sys.platform.startswith('linux') or sys.platform.startswith('darwin'),
        "Integration tests require actual platform"
    )
    def test_real_platform_detection(self):
        """Test real platform detection."""
        self.assertIn(self.installer.platform, ['windows', 'linux', 'darwin'])
        self.assertIsNotNone(self.installer.primary_manager)
    
    def test_dry_run_installation(self):
        """Test dry-run installation mode."""
        packages = ["requests", "numpy"]
        
        with patch.object(self.installer, '_install_single_package') as mock_install:
            mock_install.side_effect = [
                PackageInstallationResult("requests", True, "2.31.0", 0.0),
                PackageInstallationResult("numpy", True, "1.24.3", 0.0)
            ]
            
            results = self.installer.install_packages(packages, dry_run=True)
            
            self.assertEqual(len(results), 2)
            # In dry run, should not actually call installation
            self.assertEqual(mock_install.call_count, 0)


class TestCommandLineInterface(unittest.TestCase):
    """Test cases for command-line interface."""
    
    @patch('sys.argv', ['package_installer.py', '--help'])
    def test_help_argument(self):
        """Test help argument display."""
        with patch('builtins.print') as mock_print:
            try:
                from cross_platform.package_installer import main
                main()
            except SystemExit:
                pass  # argparse calls sys.exit after showing help
            
            # Check that help was displayed
            print_calls = [str(call) for call in mock_print.call_args_list]
            help_displayed = any('usage:' in call.lower() for call in print_calls)
            self.assertTrue(help_displayed)
    
    @patch('sys.argv', ['package_installer.py', 'requests', 'numpy', '--verbose'])
    @patch.object(CrossPlatformPackageInstaller, 'install_packages')
    def test_package_installation_command(self, mock_install):
        """Test package installation via command line."""
        mock_install.return_value = [
            PackageInstallationResult("requests", True, "2.31.0", 1.0),
            PackageInstallationResult("numpy", True, "1.24.3", 2.0)
        ]
        
        try:
            from cross_platform.package_installer import main
            main()
        except SystemExit as e:
            self.assertEqual(e.code, 0)  # Should exit successfully
        
        mock_install.assert_called_once()
        call_args = mock_install.call_args
        packages = call_args[0][0]
        self.assertIn("requests", packages)
        self.assertIn("numpy", packages)


if __name__ == '__main__':
    # Configure test discovery and execution
    unittest.main(
        verbosity=2,
        buffer=True,
        failfast=False,
        warnings='ignore'
    )