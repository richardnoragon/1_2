#!/usr/bin/env python3
"""Test suite for CrossPlatformBrowserDetector.

This module provides comprehensive tests for the browser detection
automation system across Windows, Linux, and macOS platforms.
"""

import json
import os
import platform
import subprocess
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, Mock, mock_open, patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from cross_platform.browser_detector import (BrowserInfo, BrowserProfile,
                                             CrossPlatformBrowserDetector,
                                             DetectionResult,
                                             LinuxBrowserDetector,
                                             MacOSBrowserDetector,
                                             WindowsBrowserDetector)


class TestBrowserInfo(unittest.TestCase):
    """Test cases for BrowserInfo dataclass."""
    
    def test_browser_info_creation(self):
        """Test BrowserInfo creation with all fields."""
        browser = BrowserInfo(
            name="Google Chrome",
            executable_path="/opt/google/chrome/chrome",
            version="115.0.5790.170",
            is_default=True,
            profiles=[BrowserProfile("Default", "/home/user/.config/google-chrome/Default")]
        )
        
        self.assertEqual(browser.name, "Google Chrome")
        self.assertEqual(browser.executable_path, "/opt/google/chrome/chrome")
        self.assertEqual(browser.version, "115.0.5790.170")
        self.assertTrue(browser.is_default)
        self.assertEqual(len(browser.profiles), 1)
    
    def test_browser_info_defaults(self):
        """Test BrowserInfo creation with default values."""
        browser = BrowserInfo(name="Firefox")
        
        self.assertEqual(browser.name, "Firefox")
        self.assertIsNone(browser.executable_path)
        self.assertIsNone(browser.version)
        self.assertFalse(browser.is_default)
        self.assertEqual(browser.profiles, [])


class TestBrowserProfile(unittest.TestCase):
    """Test cases for BrowserProfile dataclass."""
    
    def test_browser_profile_creation(self):
        """Test BrowserProfile creation."""
        profile = BrowserProfile(
            name="Work Profile",
            path="/home/user/.config/google-chrome/Profile 1"
        )
        
        self.assertEqual(profile.name, "Work Profile")
        self.assertEqual(profile.path, "/home/user/.config/google-chrome/Profile 1")


class TestDetectionResult(unittest.TestCase):
    """Test cases for DetectionResult dataclass."""
    
    def test_detection_result_creation(self):
        """Test DetectionResult creation."""
        browsers = [
            BrowserInfo("Chrome", "/opt/google/chrome/chrome", "115.0.0.0"),
            BrowserInfo("Firefox", "/usr/bin/firefox", "116.0.0.0")
        ]
        
        result = DetectionResult(
            platform="linux",
            browsers_found=browsers,
            default_browser="Chrome",
            detection_time=1.5,
            success=True
        )
        
        self.assertEqual(result.platform, "linux")
        self.assertEqual(len(result.browsers_found), 2)
        self.assertEqual(result.default_browser, "Chrome")
        self.assertEqual(result.detection_time, 1.5)
        self.assertTrue(result.success)
        self.assertEqual(len(result.errors), 0)


class TestWindowsBrowserDetector(unittest.TestCase):
    """Test cases for WindowsBrowserDetector."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = WindowsBrowserDetector()
    
    @patch('winreg.OpenKey')
    @patch('winreg.QueryValueEx')
    @patch('winreg.EnumKey')
    @patch('winreg.CloseKey')
    def test_detect_browsers_from_registry(self, mock_close, mock_enum, mock_query, mock_open):
        """Test browser detection from Windows registry."""
        # Mock registry structure
        mock_enum.side_effect = [
            "chrome.exe",  # First enum call
            StopIteration  # End enumeration
        ]
        
        mock_query.side_effect = [
            ("Google Chrome", 1),  # Browser name
            ("115.0.5790.170", 1),  # Version
            ("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe", 1)  # Path
        ]
        
        browsers = self.detector._detect_browsers_from_registry()
        
        self.assertGreater(len(browsers), 0)
        # Verify registry operations were called
        mock_open.assert_called()
        mock_enum.assert_called()
    
    @patch('subprocess.run')
    def test_get_default_browser(self, mock_run):
        """Test getting default browser on Windows."""
        # Mock PowerShell output for default browser
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Google Chrome"
        )
        
        default_browser = self.detector._get_default_browser()
        
        self.assertEqual(default_browser, "Google Chrome")
        # Verify PowerShell command was used
        args = mock_run.call_args[0][0]
        self.assertIn("powershell", args[0].lower())
    
    @patch('subprocess.run')
    def test_get_browser_version_success(self, mock_run):
        """Test successful browser version retrieval."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Google Chrome 115.0.5790.170"
        )
        
        version = self.detector._get_browser_version("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")
        
        self.assertEqual(version, "115.0.5790.170")
    
    @patch('subprocess.run')
    def test_get_browser_version_failure(self, mock_run):
        """Test failed browser version retrieval."""
        mock_run.side_effect = subprocess.SubprocessError("Command failed")
        
        version = self.detector._get_browser_version("C:\\NonExistent\\browser.exe")
        
        self.assertIsNone(version)
    
    @patch('pathlib.Path.exists')
    def test_find_browser_profiles_chrome(self, mock_exists):
        """Test finding Chrome profiles on Windows."""
        mock_exists.return_value = True
        
        with patch('pathlib.Path.iterdir') as mock_iterdir:
            # Mock profile directories
            mock_profile_dirs = [
                Mock(is_dir=lambda: True, name="Default"),
                Mock(is_dir=lambda: True, name="Profile 1"),
                Mock(is_dir=lambda: False, name="some_file.txt")  # Should be ignored
            ]
            mock_iterdir.return_value = mock_profile_dirs
            
            profiles = self.detector._find_browser_profiles("Chrome")
            
            self.assertEqual(len(profiles), 2)
            self.assertEqual(profiles[0].name, "Default")
            self.assertEqual(profiles[1].name, "Profile 1")
    
    @patch('pathlib.Path.exists')
    def test_find_browser_profiles_not_found(self, mock_exists):
        """Test profile finding when profile directory doesn't exist."""
        mock_exists.return_value = False
        
        profiles = self.detector._find_browser_profiles("Chrome")
        
        self.assertEqual(profiles, [])


class TestLinuxBrowserDetector(unittest.TestCase):
    """Test cases for LinuxBrowserDetector."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = LinuxBrowserDetector()
    
    @patch('pathlib.Path.glob')
    def test_detect_browsers_from_applications(self, mock_glob):
        """Test browser detection from .desktop files on Linux."""
        # Mock .desktop files
        mock_desktop_files = [
            Mock(name="google-chrome.desktop"),
            Mock(name="firefox.desktop"),
            Mock(name="microsoft-edge.desktop")
        ]
        mock_glob.return_value = mock_desktop_files
        
        with patch('builtins.open', mock_open(read_data="""[Desktop Entry]
Name=Google Chrome
Exec=/opt/google/chrome/chrome %U
Icon=google-chrome
Type=Application
Categories=Network;WebBrowser;""")):
            browsers = self.detector._detect_browsers_from_applications()
            
            # Should find browsers based on mocked desktop files
            self.assertGreater(len(browsers), 0)
    
    def test_parse_desktop_file(self):
        """Test parsing of .desktop file."""
        desktop_content = """[Desktop Entry]
Name=Google Chrome
Comment=Access the Internet
Exec=/opt/google/chrome/chrome %U
Icon=google-chrome
Terminal=false
Type=Application
Categories=Network;WebBrowser;
MimeType=text/html;text/xml;
StartupNotify=true"""
        
        with patch('builtins.open', mock_open(read_data=desktop_content)):
            browser_info = self.detector._parse_desktop_file(Path("/usr/share/applications/google-chrome.desktop"))
            
            self.assertIsNotNone(browser_info)
            self.assertEqual(browser_info.name, "Google Chrome")
            self.assertEqual(browser_info.executable_path, "/opt/google/chrome/chrome")
    
    @patch('subprocess.run')
    def test_get_default_browser_xdg_settings(self, mock_run):
        """Test getting default browser using xdg-settings."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="google-chrome.desktop"
        )
        
        default_browser = self.detector._get_default_browser()
        
        self.assertEqual(default_browser, "google-chrome.desktop")
        # Verify xdg-settings command was used
        args = mock_run.call_args[0][0]
        self.assertIn("xdg-settings", args)
    
    @patch('subprocess.run')
    def test_get_default_browser_failure(self, mock_run):
        """Test default browser detection failure."""
        mock_run.side_effect = subprocess.SubprocessError("Command failed")
        
        default_browser = self.detector._get_default_browser()
        
        self.assertIsNone(default_browser)
    
    @patch('pathlib.Path.exists')
    def test_find_browser_profiles_firefox(self, mock_exists):
        """Test finding Firefox profiles on Linux."""
        mock_exists.return_value = True
        
        with patch('pathlib.Path.iterdir') as mock_iterdir:
            # Mock profile directories
            mock_profile_dirs = [
                Mock(is_dir=lambda: True, name="default-release"),
                Mock(is_dir=lambda: True, name="dev-edition-default"),
                Mock(is_dir=lambda: False, name="profiles.ini")  # Should be ignored
            ]
            mock_iterdir.return_value = mock_profile_dirs
            
            profiles = self.detector._find_browser_profiles("Firefox")
            
            self.assertEqual(len(profiles), 2)
            profile_names = [p.name for p in profiles]
            self.assertIn("default-release", profile_names)
            self.assertIn("dev-edition-default", profile_names)


class TestMacOSBrowserDetector(unittest.TestCase):
    """Test cases for MacOSBrowserDetector."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = MacOSBrowserDetector()
    
    @patch('subprocess.run')
    def test_detect_browsers_from_mdfind(self, mock_run):
        """Test browser detection using mdfind on macOS."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="""/Applications/Google Chrome.app
/Applications/Firefox.app
/Applications/Safari.app
/Applications/Microsoft Edge.app"""
        )
        
        browsers = self.detector._detect_browsers_from_mdfind()
        
        self.assertEqual(len(browsers), 4)
        browser_names = [b.name for b in browsers]
        self.assertIn("Google Chrome", browser_names)
        self.assertIn("Firefox", browser_names)
        self.assertIn("Safari", browser_names)
        self.assertIn("Microsoft Edge", browser_names)
    
    @patch('subprocess.run')
    def test_get_default_browser_system_profiler(self, mock_run):
        """Test getting default browser using system_profiler."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Default Web Browser: Google Chrome"
        )
        
        default_browser = self.detector._get_default_browser()
        
        self.assertEqual(default_browser, "Google Chrome")
    
    @patch('subprocess.run')
    def test_get_browser_version_info_plist(self, mock_run):
        """Test getting browser version from Info.plist."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="115.0.5790.170"
        )
        
        version = self.detector._get_browser_version("/Applications/Google Chrome.app")
        
        self.assertEqual(version, "115.0.5790.170")
    
    @patch('pathlib.Path.exists')
    def test_find_browser_profiles_chrome_macos(self, mock_exists):
        """Test finding Chrome profiles on macOS."""
        mock_exists.return_value = True
        
        with patch('pathlib.Path.iterdir') as mock_iterdir:
            # Mock profile directories
            mock_profile_dirs = [
                Mock(is_dir=lambda: True, name="Default"),
                Mock(is_dir=lambda: True, name="Profile 1"),
                Mock(is_dir=lambda: False, name="Local State")  # Should be ignored
            ]
            mock_iterdir.return_value = mock_profile_dirs
            
            profiles = self.detector._find_browser_profiles("Chrome")
            
            self.assertEqual(len(profiles), 2)
            self.assertEqual(profiles[0].name, "Default")
            self.assertEqual(profiles[1].name, "Profile 1")


class TestCrossPlatformBrowserDetector(unittest.TestCase):
    """Test cases for CrossPlatformBrowserDetector."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = CrossPlatformBrowserDetector(verbose=False)
    
    @patch('platform.system')
    def test_detect_platform_windows(self, mock_system):
        """Test Windows platform detection."""
        mock_system.return_value = "Windows"
        
        detector = CrossPlatformBrowserDetector()
        
        self.assertEqual(detector.platform, "windows")
        self.assertIsInstance(detector.platform_detector, WindowsBrowserDetector)
    
    @patch('platform.system')
    def test_detect_platform_linux(self, mock_system):
        """Test Linux platform detection."""
        mock_system.return_value = "Linux"
        
        detector = CrossPlatformBrowserDetector()
        
        self.assertEqual(detector.platform, "linux")
        self.assertIsInstance(detector.platform_detector, LinuxBrowserDetector)
    
    @patch('platform.system')
    def test_detect_platform_macos(self, mock_system):
        """Test macOS platform detection."""
        mock_system.return_value = "Darwin"
        
        detector = CrossPlatformBrowserDetector()
        
        self.assertEqual(detector.platform, "darwin")
        self.assertIsInstance(detector.platform_detector, MacOSBrowserDetector)
    
    @patch.object(WindowsBrowserDetector, 'detect_browsers')
    def test_detect_browsers_success(self, mock_detect):
        """Test successful browser detection."""
        # Mock successful detection
        mock_browsers = [
            BrowserInfo("Chrome", "/path/to/chrome", "115.0.0.0", True),
            BrowserInfo("Firefox", "/path/to/firefox", "116.0.0.0", False)
        ]
        mock_detect.return_value = DetectionResult(
            platform="windows",
            browsers_found=mock_browsers,
            default_browser="Chrome",
            detection_time=1.0,
            success=True
        )
        
        with patch('platform.system', return_value="Windows"):
            detector = CrossPlatformBrowserDetector()
            result = detector.detect_browsers()
        
        self.assertTrue(result.success)
        self.assertEqual(len(result.browsers_found), 2)
        self.assertEqual(result.default_browser, "Chrome")
        self.assertEqual(result.platform, "windows")
    
    @patch.object(WindowsBrowserDetector, 'detect_browsers')
    def test_detect_browsers_failure(self, mock_detect):
        """Test failed browser detection."""
        # Mock failed detection
        mock_detect.return_value = DetectionResult(
            platform="windows",
            browsers_found=[],
            default_browser=None,
            detection_time=0.5,
            success=False,
            errors=["Registry access denied"]
        )
        
        with patch('platform.system', return_value="Windows"):
            detector = CrossPlatformBrowserDetector()
            result = detector.detect_browsers()
        
        self.assertFalse(result.success)
        self.assertEqual(len(result.browsers_found), 0)
        self.assertIsNone(result.default_browser)
        self.assertGreater(len(result.errors), 0)
    
    def test_filter_browsers_by_name(self):
        """Test filtering browsers by name."""
        browsers = [
            BrowserInfo("Google Chrome", "/path/to/chrome"),
            BrowserInfo("Mozilla Firefox", "/path/to/firefox"),
            BrowserInfo("Microsoft Edge", "/path/to/edge")
        ]
        
        chrome_browsers = self.detector._filter_browsers_by_name(browsers, ["Chrome"])
        firefox_browsers = self.detector._filter_browsers_by_name(browsers, ["Firefox"])
        multiple_browsers = self.detector._filter_browsers_by_name(browsers, ["Chrome", "Edge"])
        
        self.assertEqual(len(chrome_browsers), 1)
        self.assertEqual(chrome_browsers[0].name, "Google Chrome")
        
        self.assertEqual(len(firefox_browsers), 1)
        self.assertEqual(firefox_browsers[0].name, "Mozilla Firefox")
        
        self.assertEqual(len(multiple_browsers), 2)
        browser_names = [b.name for b in multiple_browsers]
        self.assertIn("Google Chrome", browser_names)
        self.assertIn("Microsoft Edge", browser_names)
    
    def test_get_browser_by_name(self):
        """Test getting specific browser by name."""
        browsers = [
            BrowserInfo("Google Chrome", "/path/to/chrome"),
            BrowserInfo("Mozilla Firefox", "/path/to/firefox")
        ]
        
        result = DetectionResult(
            platform="test",
            browsers_found=browsers,
            default_browser="Chrome",
            detection_time=1.0,
            success=True
        )
        
        chrome_browser = self.detector.get_browser_by_name(result, "Chrome")
        firefox_browser = self.detector.get_browser_by_name(result, "Firefox")
        nonexistent_browser = self.detector.get_browser_by_name(result, "Safari")
        
        self.assertIsNotNone(chrome_browser)
        self.assertEqual(chrome_browser.name, "Google Chrome")
        
        self.assertIsNotNone(firefox_browser)
        self.assertEqual(firefox_browser.name, "Mozilla Firefox")
        
        self.assertIsNone(nonexistent_browser)
    
    def test_get_default_browser(self):
        """Test getting default browser from results."""
        browsers = [
            BrowserInfo("Google Chrome", "/path/to/chrome", is_default=True),
            BrowserInfo("Mozilla Firefox", "/path/to/firefox", is_default=False)
        ]
        
        result = DetectionResult(
            platform="test",
            browsers_found=browsers,
            default_browser="Chrome",
            detection_time=1.0,
            success=True
        )
        
        default_browser = self.detector.get_default_browser(result)
        
        self.assertIsNotNone(default_browser)
        self.assertEqual(default_browser.name, "Google Chrome")
        self.assertTrue(default_browser.is_default)
    
    def test_generate_detection_report(self):
        """Test detection report generation."""
        browsers = [
            BrowserInfo("Google Chrome", "/path/to/chrome", "115.0.0.0", True),
            BrowserInfo("Mozilla Firefox", "/path/to/firefox", "116.0.0.0", False)
        ]
        
        result = DetectionResult(
            platform="test",
            browsers_found=browsers,
            default_browser="Chrome",
            detection_time=1.5,
            success=True
        )
        
        report = self.detector.generate_detection_report(result)
        
        self.assertIn("BROWSER DETECTION REPORT", report)
        self.assertIn("Platform: test", report)
        self.assertIn("Browsers Found: 2", report)
        self.assertIn("Default Browser: Chrome", report)
        self.assertIn("Google Chrome", report)
        self.assertIn("Mozilla Firefox", report)
        self.assertIn("115.0.0.0", report)
        self.assertIn("116.0.0.0", report)
    
    def test_export_detection_results_json(self):
        """Test exporting detection results to JSON."""
        browsers = [
            BrowserInfo("Google Chrome", "/path/to/chrome", "115.0.0.0"),
            BrowserInfo("Mozilla Firefox", "/path/to/firefox", "116.0.0.0")
        ]
        
        result = DetectionResult(
            platform="test",
            browsers_found=browsers,
            default_browser="Chrome",
            detection_time=1.0,
            success=True
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            filename = self.detector.export_detection_results(
                result, export_format="json", output_dir=temp_dir
            )
            
            self.assertTrue(os.path.exists(filename))
            self.assertTrue(filename.endswith('.json'))
            
            # Verify JSON content
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self.assertIn("detection_date", data)
            self.assertIn("platform", data)
            self.assertEqual(len(data["browsers_found"]), 2)
            self.assertEqual(data["default_browser"], "Chrome")


class TestCrossPlatformBrowserDetectorIntegration(unittest.TestCase):
    """Integration tests for CrossPlatformBrowserDetector."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.detector = CrossPlatformBrowserDetector(verbose=True)
    
    @unittest.skipUnless(
        sys.platform.startswith('win') or sys.platform.startswith('linux') or sys.platform.startswith('darwin'),
        "Integration tests require actual platform"
    )
    def test_real_platform_detection(self):
        """Test real platform detection."""
        self.assertIn(self.detector.platform, ['windows', 'linux', 'darwin'])
        self.assertIsNotNone(self.detector.platform_detector)
    
    def test_validate_browser_detection(self):
        """Test validation of browser detection results."""
        # This would be called on real detection results
        mock_result = DetectionResult(
            platform=self.detector.platform,
            browsers_found=[],
            default_browser=None,
            detection_time=0.0,
            success=True
        )
        
        # Should not raise an exception
        validated = self.detector.validate_detection_results(mock_result)
        self.assertIsNotNone(validated)


class TestCommandLineInterface(unittest.TestCase):
    """Test cases for command-line interface."""
    
    @patch('sys.argv', ['browser_detector.py', '--help'])
    def test_help_argument(self, ):
        """Test help argument display."""
        with patch('builtins.print') as mock_print:
            try:
                from cross_platform.browser_detector import main
                main()
            except SystemExit:
                pass  # argparse calls sys.exit after showing help
            
            # Check that help was displayed
            print_calls = [str(call) for call in mock_print.call_args_list]
            help_displayed = any('usage:' in call.lower() for call in print_calls)
            self.assertTrue(help_displayed)
    
    @patch('sys.argv', ['browser_detector.py', '--verbose', '--export', 'json'])
    @patch.object(CrossPlatformBrowserDetector, 'detect_browsers')
    def test_detection_command(self, mock_detect):
        """Test browser detection via command line."""
        mock_detect.return_value = DetectionResult(
            platform="test",
            browsers_found=[BrowserInfo("Chrome", "/path/to/chrome")],
            default_browser="Chrome",
            detection_time=1.0,
            success=True
        )
        
        try:
            from cross_platform.browser_detector import main
            main()
        except SystemExit as e:
            self.assertEqual(e.code, 0)  # Should exit successfully
        
        mock_detect.assert_called_once()


if __name__ == '__main__':
    # Configure test discovery and execution
    unittest.main(
        verbosity=2,
        buffer=True,
        failfast=False,
        warnings='ignore'
    )