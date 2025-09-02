"""
Enhanced comprehensive unit tests for browser_detector.py

Test suite for BrowserDetector class with full coverage of all methods,
edge cases, and platform-specific functionality with enhanced reporting.

Created: 2025-08-30
Target: browser_detector.py
"""

import datetime
import json
import os
import sys
from pathlib import Path
from typing import Dict, List
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

# Add the source directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from utilities.privacy.privacy_tools.core.browser_detector import \
        BrowserDetector
    from utilities.privacy.privacy_tools.core.data_locations import \
        DataLocations
    from utilities.privacy.privacy_tools.core.platform_utils import \
        PlatformUtils
    IMPORTS_AVAILABLE = True
except ImportError as e:
    IMPORTS_AVAILABLE = False
    pytest.skip(f"Required modules not available: {e}", allow_module_level=True)


class TestBrowserDetectorEnhanced:
    """Enhanced test class for BrowserDetector with comprehensive coverage."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup method that runs before each test."""
        if IMPORTS_AVAILABLE:
            self.detector = BrowserDetector()
            # Reset cached values
            self.detector._detected_browsers = None
            self.detector._browser_paths = {}
        
    def teardown_method(self):
        """Teardown method that runs after each test."""
        if IMPORTS_AVAILABLE:
            # Clean up any cached values
            if hasattr(self.detector, '_detected_browsers'):
                self.detector._detected_browsers = None
            if hasattr(self.detector, '_browser_paths'):
                self.detector._browser_paths.clear()

    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    def test_init_basic(self):
        """Test BrowserDetector initialization."""
        detector = BrowserDetector()
        assert detector.platform is not None
        assert detector._detected_browsers is None
        assert detector._browser_paths == {}

    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    @patch('utilities.privacy.privacy_tools.core.browser_detector.PlatformUtils.get_platform')
    def test_init_with_platform_mock(self, mock_platform):
        """Test initialization with mocked platform."""
        mock_platform.return_value = "windows"
        detector = BrowserDetector()
        assert detector.platform == "windows"

    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    @patch('utilities.privacy.privacy_tools.core.browser_detector.DataLocations.get_all_supported_browsers')
    @patch.object(BrowserDetector, '_is_browser_installed')
    def test_detect_installed_browsers_first_call_success(self, mock_is_installed, mock_supported):
        """Test detect_installed_browsers on first successful call."""
        mock_supported.return_value = ["chrome", "firefox", "edge"]
        mock_is_installed.side_effect = [True, False, True]
        
        result = self.detector.detect_installed_browsers()
        
        assert result == ["chrome", "edge"]
        assert self.detector._detected_browsers == ["chrome", "edge"]
        mock_supported.assert_called_once()
        assert mock_is_installed.call_count == 3

    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    def test_detect_installed_browsers_cached_result(self):
        """Test detect_installed_browsers returns cached result."""
        self.detector._detected_browsers = ["chrome", "firefox"]
        
        with patch.object(self.detector, '_is_browser_installed') as mock_is_installed:
            result = self.detector.detect_installed_browsers()
            
            assert result == ["chrome", "firefox"]
            mock_is_installed.assert_not_called()

    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    @patch('utilities.privacy.privacy_tools.core.browser_detector.PlatformUtils.get_platform')
    @patch.object(BrowserDetector, '_check_windows_browser')
    def test_is_browser_installed_windows_platform(self, mock_check_windows, mock_platform):
        """Test _is_browser_installed for Windows platform."""
        mock_platform.return_value = "windows"
        mock_check_windows.return_value = True
        
        result = self.detector._is_browser_installed("chrome")
        
        assert result is True
        mock_check_windows.assert_called_once_with("chrome")

    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    @patch('utilities.privacy.privacy_tools.core.browser_detector.PlatformUtils.get_platform')
    @patch.object(BrowserDetector, '_check_macos_browser')
    def test_is_browser_installed_macos_platform(self, mock_check_macos, mock_platform):
        """Test _is_browser_installed for macOS platform."""
        mock_platform.return_value = "darwin"
        mock_check_macos.return_value = False
        
        result = self.detector._is_browser_installed("safari")
        
        assert result is False
        mock_check_macos.assert_called_once_with("safari")

    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    @patch('utilities.privacy.privacy_tools.core.browser_detector.PlatformUtils.get_platform')
    @patch.object(BrowserDetector, '_check_linux_browser')
    def test_is_browser_installed_linux_platform(self, mock_check_linux, mock_platform):
        """Test _is_browser_installed for Linux platform."""
        mock_platform.return_value = "linux"
        mock_check_linux.return_value = True
        
        result = self.detector._is_browser_installed("firefox")
        
        assert result is True
        mock_check_linux.assert_called_once_with("firefox")

    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    @patch('utilities.privacy.privacy_tools.core.browser_detector.PlatformUtils.get_platform')
    def test_is_browser_installed_unknown_platform(self, mock_platform):
        """Test _is_browser_installed for unknown platform."""
        mock_platform.return_value = "unknown_os"
        
        result = self.detector._is_browser_installed("chrome")
        
        assert result is False

    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    @patch('utilities.privacy.privacy_tools.core.browser_detector.PlatformUtils.get_home_directory')
    @patch('utilities.privacy.privacy_tools.core.browser_detector.PlatformUtils.get_local_appdata_directory')
    @patch('utilities.privacy.privacy_tools.core.browser_detector.PlatformUtils.get_appdata_directory')
    def test_check_windows_browser_chrome_exists(self, mock_appdata, mock_local_appdata, mock_home):
        """Test _check_windows_browser for Chrome when it exists."""
        mock_home.return_value = Path("C:/Users/Test")
        mock_local_appdata.return_value = Path("C:/Users/Test/AppData/Local")
        mock_appdata.return_value = Path("C:/Users/Test/AppData/Roaming")
        
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = True
            
            if IMPORTS_AVAILABLE:
                result = self.detector._check_windows_browser(DataLocations.CHROME)
                assert result is True

    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    @patch('utilities.privacy.privacy_tools.core.browser_detector.PlatformUtils.get_home_directory')
    @patch('utilities.privacy.privacy_tools.core.browser_detector.PlatformUtils.get_local_appdata_directory')
    @patch('utilities.privacy.privacy_tools.core.browser_detector.PlatformUtils.get_appdata_directory')
    def test_check_windows_browser_firefox_exists(self, mock_appdata, mock_local_appdata, mock_home):
        """Test _check_windows_browser for Firefox when it exists."""
        mock_home.return_value = Path("C:/Users/Test")
        mock_local_appdata.return_value = Path("C:/Users/Test/AppData/Local")
        mock_appdata.return_value = Path("C:/Users/Test/AppData/Roaming")
        
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = True
            
            if IMPORTS_AVAILABLE:
                result = self.detector._check_windows_browser(DataLocations.FIREFOX)
                assert result is True

    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    @patch('utilities.privacy.privacy_tools.core.browser_detector.PlatformUtils.get_home_directory')
    @patch('utilities.privacy.privacy_tools.core.browser_detector.PlatformUtils.get_local_appdata_directory')
    @patch('utilities.privacy.privacy_tools.core.browser_detector.PlatformUtils.get_appdata_directory')
    def test_check_windows_browser_edge_exists(self, mock_appdata, mock_local_appdata, mock_home):
        """Test _check_windows_browser for Edge when it exists."""
        mock_home.return_value = Path("C:/Users/Test")
        mock_local_appdata.return_value = Path("C:/Users/Test/AppData/Local")
        mock_appdata.return_value = Path("C:/Users/Test/AppData/Roaming")
        
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = True
            
            if IMPORTS_AVAILABLE:
                result = self.detector._check_windows_browser(DataLocations.EDGE)
                assert result is True

    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    @patch('utilities.privacy.privacy_tools.core.browser_detector.PlatformUtils.get_home_directory')
    @patch('utilities.privacy.privacy_tools.core.browser_detector.PlatformUtils.get_local_appdata_directory')
    @patch('utilities.privacy.privacy_tools.core.browser_detector.PlatformUtils.get_appdata_directory')
    def test_check_windows_browser_no_appdata_directories(self, mock_appdata, mock_local_appdata, mock_home):
        """Test _check_windows_browser when appdata directories are None."""
        mock_home.return_value = Path("C:/Users/Test")
        mock_local_appdata.return_value = None
        mock_appdata.return_value = None
        
        if IMPORTS_AVAILABLE:
            result = self.detector._check_windows_browser(DataLocations.CHROME)
            assert result is False

    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    @patch('utilities.privacy.privacy_tools.core.browser_detector.PlatformUtils.get_home_directory')
    def test_check_macos_browser_chrome_app_directory(self, mock_home):
        """Test _check_macos_browser for Chrome application directory."""
        mock_home.return_value = Path("/Users/test")
        
        with patch('pathlib.Path.exists') as mock_exists:
            # First call returns True (Chrome app exists)
            mock_exists.return_value = True
            
            if IMPORTS_AVAILABLE:
                result = self.detector._check_macos_browser(DataLocations.CHROME)
                assert result is True

    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    @patch('utilities.privacy.privacy_tools.core.browser_detector.PlatformUtils.get_home_directory')
    def test_check_macos_browser_safari_exists(self, mock_home):
        """Test _check_macos_browser for Safari when it exists."""
        mock_home.return_value = Path("/Users/test")
        
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = True
            
            if IMPORTS_AVAILABLE:
                result = self.detector._check_macos_browser(DataLocations.SAFARI)
                assert result is True

    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    @patch('utilities.privacy.privacy_tools.core.browser_detector.PlatformUtils.get_home_directory')
    def test_check_linux_browser_chrome_config_directory(self, mock_home):
        """Test _check_linux_browser for Chrome config directory."""
        mock_home.return_value = Path("/home/test")
        
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = True
            
            if IMPORTS_AVAILABLE:
                result = self.detector._check_linux_browser(DataLocations.CHROME)
                assert result is True

    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    @patch('shutil.which')
    def test_check_command_exists_found(self, mock_which):
        """Test _check_command_exists when command is found."""
        mock_which.return_value = "/usr/bin/firefox"
        
        result = self.detector._check_command_exists("firefox")
        
        assert result is True
        mock_which.assert_called_once_with("firefox")

    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    @patch('shutil.which')
    def test_check_command_exists_not_found(self, mock_which):
        """Test _check_command_exists when command is not found."""
        mock_which.return_value = None
        
        result = self.detector._check_command_exists("nonexistent")
        
        assert result is False
        mock_which.assert_called_once_with("nonexistent")

    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    @patch.object(BrowserDetector, 'detect_installed_browsers')
    @patch('utilities.privacy.privacy_tools.core.browser_detector.DataLocations.get_browser_executable_names')
    @patch('utilities.privacy.privacy_tools.core.browser_detector.PlatformUtils.is_process_running')
    def test_get_running_browsers_with_running_processes(self, mock_is_running, mock_exe_names, mock_detect):
        """Test get_running_browsers with running browser processes."""
        mock_detect.return_value = ["chrome", "firefox"]
        mock_exe_names.return_value = {
            "chrome": ["chrome.exe", "google-chrome"],
            "firefox": ["firefox.exe", "firefox"]
        }
        mock_is_running.side_effect = [True, False, False, True]
        
        result = self.detector.get_running_browsers()
        
        assert result == ["chrome", "firefox"]
        assert mock_is_running.call_count == 4

    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    @patch.object(BrowserDetector, 'get_running_browsers')
    def test_is_browser_running_positive_case(self, mock_running):
        """Test is_browser_running when browser is actually running."""
        mock_running.return_value = ["chrome", "firefox"]
        
        result = self.detector.is_browser_running("chrome")
        
        assert result is True

    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    @patch.object(BrowserDetector, 'get_running_browsers')
    def test_is_browser_running_negative_case(self, mock_running):
        """Test is_browser_running when browser is not running."""
        mock_running.return_value = ["firefox"]
        
        result = self.detector.is_browser_running("chrome")
        
        assert result is False

    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    @patch.object(BrowserDetector, 'is_browser_running')
    def test_close_browser_not_running(self, mock_is_running):
        """Test close_browser when browser is not running."""
        mock_is_running.return_value = False
        
        result = self.detector.close_browser("chrome")
        
        assert result is True

    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    @patch('utilities.privacy.privacy_tools.core.browser_detector.DataLocations.get_browser_data_paths')
    def test_get_browser_data_paths_new_browser(self, mock_get_paths):
        """Test get_browser_data_paths for a new browser."""
        expected_paths = {"profiles": [Path("/test/profile")]}
        mock_get_paths.return_value = expected_paths
        
        result = self.detector.get_browser_data_paths("chrome")
        
        assert result == expected_paths
        assert self.detector._browser_paths["chrome"] == expected_paths
        mock_get_paths.assert_called_once_with("chrome")

    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    @patch.object(BrowserDetector, 'get_browser_data_paths')
    def test_get_browser_profile_paths_with_profiles(self, mock_data_paths):
        """Test get_browser_profile_paths when profiles exist."""
        profiles = [Path("/test/profile1"), Path("/test/profile2")]
        mock_data_paths.return_value = {"profiles": profiles, "cache": [Path("/test/cache")]}
        
        result = self.detector.get_browser_profile_paths("chrome")
        
        assert result == profiles

    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    @patch.object(BrowserDetector, 'get_browser_data_paths')
    def test_validate_browser_access_file_accessible(self, mock_data_paths):
        """Test validate_browser_access for accessible files."""
        test_file = Path("/test/file.db")
        mock_data_paths.return_value = {"history": [test_file]}
        
        with patch('pathlib.Path.exists') as mock_exists, \
             patch('pathlib.Path.is_file') as mock_is_file, \
             patch('builtins.open', mock_open(read_data=b"test")):
            
            mock_exists.return_value = True
            mock_is_file.return_value = True
            
            result = self.detector.validate_browser_access("chrome")
            
            assert result == {"history": True}

    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    @patch.object(BrowserDetector, 'detect_installed_browsers')
    @patch.object(BrowserDetector, 'is_browser_running')
    @patch.object(BrowserDetector, 'get_browser_data_paths')
    @patch.object(BrowserDetector, 'validate_browser_access')
    def test_get_browser_info_comprehensive(self, mock_validate, mock_data_paths, mock_running, mock_detect):
        """Test get_browser_info method with all data."""
        mock_detect.return_value = ["chrome", "firefox"]
        mock_running.return_value = True
        mock_data_paths.return_value = {"profiles": [Path("/test/profile")]}
        mock_validate.return_value = {"profiles": True}
        
        result = self.detector.get_browser_info("chrome")
        
        expected = {
            "name": "chrome",
            "installed": True,
            "running": True,
            "data_paths": {"profiles": [Path("/test/profile")]},
            "access_status": {"profiles": True}
        }
        
        assert result == expected

    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    def test_refresh_detection_clears_cache(self):
        """Test refresh_detection clears all cached data."""
        # Set some cached data
        self.detector._detected_browsers = ["chrome"]
        self.detector._browser_paths = {"chrome": {"profiles": []}}
        
        self.detector.refresh_detection()
        
        assert self.detector._detected_browsers is None
        assert self.detector._browser_paths == {}

    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    def test_edge_case_empty_browser_name(self):
        """Test methods with empty browser name."""
        result = self.detector._is_browser_installed("")
        assert result is False
        
        result = self.detector.is_browser_running("")
        assert result is False

    @pytest.mark.skipif(not IMPORTS_AVAILABLE, reason="Required modules not available")
    @patch.object(BrowserDetector, '_is_browser_installed')
    def test_detect_installed_browsers_empty_result(self, mock_is_installed):
        """Test detect_installed_browsers when no browsers are installed."""
        mock_is_installed.return_value = False
        
        with patch('utilities.privacy.privacy_tools.core.browser_detector.DataLocations.get_all_supported_browsers') as mock_supported:
            mock_supported.return_value = ["chrome", "firefox"]
            
            result = self.detector.detect_installed_browsers()
            
            assert result == []
            assert self.detector._detected_browsers == []

    def test_module_imports_availability(self):
        """Test that all required modules can be imported successfully."""
        if IMPORTS_AVAILABLE:
            import utilities.privacy.privacy_tools.core.browser_detector
            import utilities.privacy.privacy_tools.core.data_locations
            import utilities.privacy.privacy_tools.core.platform_utils
            
            assert hasattr(utilities.privacy.privacy_tools.core.browser_detector, 'BrowserDetector')
            assert hasattr(utilities.privacy.privacy_tools.core.platform_utils, 'PlatformUtils')
            assert hasattr(utilities.privacy.privacy_tools.core.data_locations, 'DataLocations')
        else:
            pytest.skip("Required modules not available for import test")


@pytest.fixture(scope="session")
def test_results_directory():
    """Create and return the test results directory."""
    results_dir = Path("C:/Users/richardi/1_2/tests/unit/results")
    results_dir.mkdir(exist_ok=True)
    return results_dir


@pytest.fixture(scope="session")
def test_execution_timestamp():
    """Provide execution timestamp for test results."""
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )


def pytest_runtest_setup(item):
    """Setup for each test run."""
    if "integration" in item.keywords and not item.config.getoption("--run-integration"):
        pytest.skip("integration tests not requested")


if __name__ == "__main__":
    # Run tests with comprehensive reporting
    pytest.main([
        __file__,
        "-v",
        "--tb=long",
        "--strict-markers",
        f"--html=C:/Users/richardi/1_2/tests/unit/results/result_browser_detector_enhanced_2025-08-30.html",
        f"--json-report",
        f"--json-report-file=C:/Users/richardi/1_2/tests/unit/results/result_browser_detector_enhanced_2025-08-30.json",
        "--cov=utilities.privacy.privacy_tools.core.browser_detector",
        f"--cov-report=html:C:/Users/richardi/1_2/tests/unit/results/coverage_browser_detector_enhanced_2025-08-30",
        f"--cov-report=json:C:/Users/richardi/1_2/tests/unit/results/coverage_browser_detector_enhanced_2025-08-30.json"
    ])