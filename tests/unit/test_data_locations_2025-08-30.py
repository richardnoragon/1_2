"""
Comprehensive unit tests for data_locations.py module.

This module provides comprehensive testing for the DataLocations class,
covering all methods, edge cases, and cross-platform functionality.

Test execution: pytest test_data_locations_2025-08-30.py -v --html=result_data_locations_2025-08-30.html --json-report --json-report-file=result_data_locations_2025-08-30.json
"""

import json
import os
import platform
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add the source directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from utilities.privacy.privacy_tools.core.data_locations import DataLocations
from utilities.privacy.privacy_tools.core.platform_utils import PlatformUtils


class TestDataLocations:
    """Test suite for DataLocations class."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup method run before each test."""
        self.test_start_time = datetime.now()
        self.mock_home = Path("/test/home")
        self.mock_appdata = Path("/test/appdata")
        self.mock_local_appdata = Path("/test/local_appdata")
        
        # Reset any class variables
        pass
    
    def teardown_method(self):
        """Teardown method run after each test."""
        self.test_end_time = datetime.now()
        self.test_duration = self.test_end_time - self.test_start_time
    
    # Test class constants
    def test_browser_constants(self):
        """Test that all browser constants are properly defined."""
        assert DataLocations.CHROME == "chrome"
        assert DataLocations.FIREFOX == "firefox"
        assert DataLocations.EDGE == "edge"
        assert DataLocations.SAFARI == "safari"
        assert DataLocations.OPERA == "opera"
        assert DataLocations.BRAVE == "brave"
    
    # Test get_browser_data_paths method
    @patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_platform')
    def test_get_browser_data_paths_windows(self, mock_platform):
        """Test get_browser_data_paths for Windows platform."""
        mock_platform.return_value = PlatformUtils.WINDOWS
        
        with patch.object(DataLocations, '_get_windows_browser_paths') as mock_windows:
            mock_windows.return_value = {"test": "data"}
            result = DataLocations.get_browser_data_paths("chrome")
            mock_windows.assert_called_once_with("chrome")
            assert result == {"test": "data"}
    
    @patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_platform')
    def test_get_browser_data_paths_macos(self, mock_platform):
        """Test get_browser_data_paths for macOS platform."""
        mock_platform.return_value = PlatformUtils.MACOS
        
        with patch.object(DataLocations, '_get_macos_browser_paths') as mock_macos:
            mock_macos.return_value = {"test": "data"}
            result = DataLocations.get_browser_data_paths("firefox")
            mock_macos.assert_called_once_with("firefox")
            assert result == {"test": "data"}
    
    @patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_platform')
    def test_get_browser_data_paths_linux(self, mock_platform):
        """Test get_browser_data_paths for Linux platform."""
        mock_platform.return_value = PlatformUtils.LINUX
        
        with patch.object(DataLocations, '_get_linux_browser_paths') as mock_linux:
            mock_linux.return_value = {"test": "data"}
            result = DataLocations.get_browser_data_paths("edge")
            mock_linux.assert_called_once_with("edge")
            assert result == {"test": "data"}
    
    @patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_platform')
    def test_get_browser_data_paths_unknown_platform(self, mock_platform):
        """Test get_browser_data_paths for unknown platform."""
        mock_platform.return_value = "unknown"
        result = DataLocations.get_browser_data_paths("chrome")
        assert result == {}
    
    # Test _get_windows_browser_paths method
    @patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory')
    @patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_local_appdata_directory')
    @patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_appdata_directory')
    def test_get_windows_browser_paths_chrome(self, mock_appdata, mock_local_appdata, mock_home):
        """Test Windows Chrome browser paths."""
        mock_home.return_value = self.mock_home
        mock_local_appdata.return_value = self.mock_local_appdata
        mock_appdata.return_value = self.mock_appdata
        
        result = DataLocations._get_windows_browser_paths("chrome")
        
        expected_base = self.mock_local_appdata / "Google" / "Chrome" / "User Data"
        assert "profiles" in result
        assert "cookies" in result
        assert "history" in result
        assert "downloads" in result
        assert "cache" in result
        assert "sessions" in result
        
        assert expected_base / "Default" in result["profiles"]
        assert expected_base / "Profile 1" in result["profiles"]
    
    @patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory')
    @patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_local_appdata_directory')
    @patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_appdata_directory')
    def test_get_windows_browser_paths_firefox(self, mock_appdata, mock_local_appdata, mock_home):
        """Test Windows Firefox browser paths."""
        mock_home.return_value = self.mock_home
        mock_local_appdata.return_value = self.mock_local_appdata
        mock_appdata.return_value = self.mock_appdata
        
        # Mock Firefox profile directory structure with proper Path objects
        base_path = self.mock_appdata / "Mozilla" / "Firefox" / "Profiles"
        mock_profile1 = Path("/test/profile1.default")
        mock_profile2 = Path("/test/profile2.default")
        
        with patch.object(Path, 'exists', return_value=True), \
             patch.object(Path, 'iterdir', return_value=[mock_profile1, mock_profile2]), \
             patch.object(Path, 'is_dir', return_value=True):
            
            result = DataLocations._get_windows_browser_paths("firefox")
            
            assert "profiles" in result
            assert "cookies" in result
            assert "history" in result
            assert "downloads" in result
            assert "cache" in result
            assert "sessions" in result
    
    @patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory')
    @patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_local_appdata_directory')
    @patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_appdata_directory')
    def test_get_windows_browser_paths_edge(self, mock_appdata, mock_local_appdata, mock_home):
        """Test Windows Edge browser paths."""
        mock_home.return_value = self.mock_home
        mock_local_appdata.return_value = self.mock_local_appdata
        mock_appdata.return_value = self.mock_appdata
        
        result = DataLocations._get_windows_browser_paths("edge")
        
        expected_base = self.mock_local_appdata / "Microsoft" / "Edge" / "User Data"
        assert "profiles" in result
        assert "cookies" in result
        assert "history" in result
        assert "downloads" in result
        assert "cache" in result
        assert "sessions" in result
        
        assert expected_base / "Default" in result["profiles"]
    
    def test_get_windows_browser_paths_unsupported_browser(self):
        """Test Windows paths for unsupported browser."""
        result = DataLocations._get_windows_browser_paths("unsupported_browser")
        assert result == {}
    
    # Test _get_macos_browser_paths method
    @patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory')
    def test_get_macos_browser_paths_chrome(self, mock_home):
        """Test macOS Chrome browser paths."""
        mock_home.return_value = self.mock_home
        
        result = DataLocations._get_macos_browser_paths("chrome")
        
        expected_base = self.mock_home / "Library" / "Application Support" / "Google" / "Chrome"
        assert "profiles" in result
        assert "cookies" in result
        assert "history" in result
        assert "downloads" in result
        assert "cache" in result
        assert "sessions" in result
        
        assert expected_base / "Default" in result["profiles"]
        assert expected_base / "Profile 1" in result["profiles"]
    
    @patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory')
    def test_get_macos_browser_paths_safari(self, mock_home):
        """Test macOS Safari browser paths."""
        mock_home.return_value = self.mock_home
        
        result = DataLocations._get_macos_browser_paths("safari")
        
        expected_base = self.mock_home / "Library" / "Safari"
        assert "profiles" in result
        assert "cookies" in result
        assert "history" in result
        assert "downloads" in result
        assert "cache" in result
        assert "sessions" in result
        
        assert expected_base in result["profiles"]
        assert expected_base / "Cookies" / "Cookies.binarycookies" in result["cookies"]
    
    @patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory')
    def test_get_macos_browser_paths_firefox(self, mock_home):
        """Test macOS Firefox browser paths."""
        mock_home.return_value = self.mock_home
        
        # Mock Firefox profile directory structure with proper Path objects
        mock_profile1 = Path("/test/profile1.default")
        mock_profile2 = Path("/test/profile2.default")
        
        with patch.object(Path, 'exists', return_value=True), \
             patch.object(Path, 'iterdir', return_value=[mock_profile1, mock_profile2]), \
             patch.object(Path, 'is_dir', return_value=True):
            
            result = DataLocations._get_macos_browser_paths("firefox")
            
            assert "profiles" in result
            assert "cookies" in result
            assert "history" in result
            assert "downloads" in result
            assert "cache" in result
            assert "sessions" in result
    
    def test_get_macos_browser_paths_unsupported_browser(self):
        """Test macOS paths for unsupported browser."""
        result = DataLocations._get_macos_browser_paths("unsupported_browser")
        assert result == {}
    
    # Test _get_linux_browser_paths method
    @patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory')
    def test_get_linux_browser_paths_chrome(self, mock_home):
        """Test Linux Chrome browser paths."""
        mock_home.return_value = self.mock_home
        
        result = DataLocations._get_linux_browser_paths("chrome")
        
        expected_base = self.mock_home / ".config" / "google-chrome"
        assert "profiles" in result
        assert "cookies" in result
        assert "history" in result
        assert "downloads" in result
        assert "cache" in result
        assert "sessions" in result
        
        assert expected_base / "Default" in result["profiles"]
        assert expected_base / "Profile 1" in result["profiles"]
    
    @patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory')
    def test_get_linux_browser_paths_firefox(self, mock_home):
        """Test Linux Firefox browser paths."""
        mock_home.return_value = self.mock_home
        
        # Create mock profile directories that behave like Path objects but can be modified
        class MockProfile:
            def __init__(self, path, name):
                self._path = Path(path)
                self.name = name
            
            def is_dir(self):
                return True
            
            def __truediv__(self, other):
                return self._path / other
        
        mock_profile1 = MockProfile("/test/profile1.default", "profile1.default")
        mock_profile2 = MockProfile("/test/profile2.default", "profile2.default")
        
        with patch.object(Path, 'exists', return_value=True), \
             patch.object(Path, 'iterdir', return_value=[mock_profile1, mock_profile2]):
            
            result = DataLocations._get_linux_browser_paths("firefox")
            
            assert "profiles" in result
            assert "cookies" in result
            assert "history" in result
            assert "downloads" in result
            assert "cache" in result
            assert "sessions" in result
    
    @patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory')
    def test_get_linux_browser_paths_edge(self, mock_home):
        """Test Linux Edge browser paths."""
        mock_home.return_value = self.mock_home
        
        result = DataLocations._get_linux_browser_paths("edge")
        
        expected_base = self.mock_home / ".config" / "microsoft-edge"
        assert "profiles" in result
        assert "cookies" in result
        assert "history" in result
        assert "downloads" in result
        assert "cache" in result
        assert "sessions" in result
        
        assert expected_base / "Default" in result["profiles"]
    
    def test_get_linux_browser_paths_unsupported_browser(self):
        """Test Linux paths for unsupported browser."""
        result = DataLocations._get_linux_browser_paths("unsupported_browser")
        assert result == {}
    
    # Test get_system_data_paths method
    @patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_platform')
    @patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory')
    @patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_appdata_directory')
    @patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_local_appdata_directory')
    @patch('os.environ.get')
    def test_get_system_data_paths_windows(self, mock_env_get, mock_local_appdata, 
                                          mock_appdata, mock_home, mock_platform):
        """Test system data paths for Windows."""
        mock_platform.return_value = PlatformUtils.WINDOWS
        mock_home.return_value = self.mock_home
        mock_appdata.return_value = self.mock_appdata
        mock_local_appdata.return_value = self.mock_local_appdata
        mock_env_get.return_value = "/temp"
        
        result = DataLocations.get_system_data_paths()
        
        assert "recent_files" in result
        assert "jump_lists" in result
        assert "thumbnail_cache" in result
        assert "temp_files" in result
        
        assert self.mock_appdata / "Microsoft" / "Windows" / "Recent" in result["recent_files"]
        assert self.mock_local_appdata / "Microsoft" / "Windows" / "Explorer" in result["thumbnail_cache"]
    
    @patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_platform')
    @patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory')
    def test_get_system_data_paths_macos(self, mock_home, mock_platform):
        """Test system data paths for macOS."""
        mock_platform.return_value = PlatformUtils.MACOS
        mock_home.return_value = self.mock_home
        
        result = DataLocations.get_system_data_paths()
        
        assert "recent_files" in result
        assert "spotlight_cache" in result
        assert "quicklook_cache" in result
        assert "temp_files" in result
        
        expected_recent = self.mock_home / "Library" / "Application Support" / "com.apple.sharedfilelist"
        assert expected_recent in result["recent_files"]
    
    @patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_platform')
    @patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory')
    def test_get_system_data_paths_linux(self, mock_home, mock_platform):
        """Test system data paths for Linux."""
        mock_platform.return_value = PlatformUtils.LINUX
        mock_home.return_value = self.mock_home
        
        result = DataLocations.get_system_data_paths()
        
        assert "recent_files" in result
        assert "thumbnail_cache" in result
        assert "temp_files" in result
        
        expected_recent = self.mock_home / ".local" / "share" / "recently-used.xbel"
        assert expected_recent in result["recent_files"]
    
    @patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_platform')
    def test_get_system_data_paths_unknown_platform(self, mock_platform):
        """Test system data paths for unknown platform."""
        mock_platform.return_value = "unknown"
        
        result = DataLocations.get_system_data_paths()
        assert result == {}
    
    # Test get_all_supported_browsers method
    def test_get_all_supported_browsers(self):
        """Test getting all supported browsers."""
        result = DataLocations.get_all_supported_browsers()
        
        expected_browsers = ["chrome", "firefox", "edge", "safari", "opera", "brave"]
        assert result == expected_browsers
        assert len(result) == 6
        assert all(isinstance(browser, str) for browser in result)
    
    # Test get_browser_executable_names method
    def test_get_browser_executable_names(self):
        """Test getting browser executable names."""
        result = DataLocations.get_browser_executable_names()
        
        assert isinstance(result, dict)
        assert "chrome" in result
        assert "firefox" in result
        assert "edge" in result
        assert "safari" in result
        assert "opera" in result
        assert "brave" in result
        
        # Test specific executable names
        assert "chrome.exe" in result["chrome"]
        assert "firefox.exe" in result["firefox"]
        assert "msedge.exe" in result["edge"]
        assert "Safari" in result["safari"]
        assert "opera.exe" in result["opera"]
        assert "brave.exe" in result["brave"]
    
    # Edge cases and error handling tests
    def test_firefox_profile_directory_not_exists(self):
        """Test Firefox paths when profile directory doesn't exist."""
        with patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory') as mock_home, \
             patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_appdata_directory') as mock_appdata:
            
            mock_home.return_value = self.mock_home
            mock_appdata.return_value = self.mock_appdata
            
            # Mock profile directory not existing
            with patch.object(Path, 'exists', return_value=False):
                result = DataLocations._get_windows_browser_paths("firefox")
                assert result == {}
    
    def test_empty_profile_directory(self):
        """Test handling of empty Firefox profile directory."""
        with patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory') as mock_home, \
             patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_appdata_directory') as mock_appdata:
            
            mock_home.return_value = self.mock_home
            mock_appdata.return_value = self.mock_appdata
            
            # Mock empty profile directory
            with patch.object(Path, 'exists', return_value=True), \
                 patch.object(Path, 'iterdir', return_value=[]):
                
                result = DataLocations._get_windows_browser_paths("firefox")
                
                assert "profiles" in result
                assert result["profiles"] == []
                assert result["cookies"] == []
    
    def test_path_with_special_characters(self):
        """Test handling paths with special characters."""
        special_home = Path("/test/home with spaces/user@domain")
        
        with patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory') as mock_home, \
             patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_local_appdata_directory') as mock_local:
            
            mock_home.return_value = special_home
            mock_local.return_value = special_home / "AppData" / "Local"
            
            result = DataLocations._get_windows_browser_paths("chrome")
            
            assert "profiles" in result
            # Verify paths are properly constructed with special characters
            expected_base = special_home / "AppData" / "Local" / "Google" / "Chrome" / "User Data"
            assert expected_base / "Default" in result["profiles"]
    
    # Performance and boundary tests
    def test_large_profile_directory(self):
        """Test handling of directory with many profiles."""
        with patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory') as mock_home, \
             patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_appdata_directory') as mock_appdata:
            
            mock_home.return_value = self.mock_home
            mock_appdata.return_value = self.mock_appdata
            
            # Create mock profile directories that behave like Path objects
            class MockProfile:
                def __init__(self, path, name):
                    self._path = Path(path)
                    self.name = name
                
                def is_dir(self):
                    return True
                
                def __truediv__(self, other):
                    return self._path / other
            
            # Create many mock profiles
            mock_profiles = []
            for i in range(100):
                profile = MockProfile(f"/test/profile{i}.default", f"profile{i}.default")
                mock_profiles.append(profile)
            
            with patch.object(Path, 'exists', return_value=True), \
                 patch.object(Path, 'iterdir', return_value=mock_profiles):
                
                result = DataLocations._get_windows_browser_paths("firefox")
                
                assert len(result["profiles"]) == 100
                assert len(result["cookies"]) == 100
    
    def test_none_values_handling(self):
        """Test handling of None values from platform utilities."""
        with patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory') as mock_home, \
             patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_appdata_directory') as mock_appdata:
            
            mock_home.return_value = None
            mock_appdata.return_value = None
            
            # Should handle gracefully without crashing
            try:
                result = DataLocations._get_windows_browser_paths("chrome")
                # The method should either return empty dict or handle None gracefully
                assert isinstance(result, dict)
            except Exception as e:
                # If an exception occurs, it should be a specific, expected type
                assert isinstance(e, (TypeError, AttributeError))
    
    # Integration tests
    @patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_platform')
    def test_integration_full_workflow(self, mock_platform):
        """Test full workflow integration."""
        mock_platform.return_value = PlatformUtils.WINDOWS
        
        # Get all supported browsers
        browsers = DataLocations.get_all_supported_browsers()
        
        # Test getting paths for each browser
        with patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory') as mock_home, \
             patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_local_appdata_directory') as mock_local, \
             patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_appdata_directory') as mock_appdata:
            
            mock_home.return_value = self.mock_home
            mock_local.return_value = self.mock_local_appdata
            mock_appdata.return_value = self.mock_appdata
            
            for browser in browsers:
                if browser in ["chrome", "edge"]:  # Browsers with full Windows support
                    result = DataLocations.get_browser_data_paths(browser)
                    assert isinstance(result, dict)
                    if result:  # If paths are returned
                        assert "profiles" in result or len(result) == 0
    
    # Parameterized tests
    @pytest.mark.parametrize("browser,expected_keys", [
        ("chrome", ["profiles", "cookies", "history", "downloads", "cache", "sessions"]),
        ("firefox", ["profiles", "cookies", "history", "downloads", "cache", "sessions"]),
        ("edge", ["profiles", "cookies", "history", "downloads", "cache", "sessions"]),
    ])
    def test_windows_browser_paths_keys(self, browser, expected_keys):
        """Test that Windows browser paths contain expected keys."""
        with patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory') as mock_home, \
             patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_local_appdata_directory') as mock_local, \
             patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_appdata_directory') as mock_appdata:
            
            mock_home.return_value = self.mock_home
            mock_local.return_value = self.mock_local_appdata
            mock_appdata.return_value = self.mock_appdata
            
            if browser == "firefox":
                # Mock Firefox profile directory with Path objects
                mock_profile = Path("/test/profile.default")
                with patch.object(Path, 'exists', return_value=True), \
                     patch.object(Path, 'iterdir', return_value=[mock_profile]), \
                     patch.object(Path, 'is_dir', return_value=True):
                    result = DataLocations._get_windows_browser_paths(browser)
            else:
                result = DataLocations._get_windows_browser_paths(browser)
            
            for key in expected_keys:
                assert key in result, f"Key '{key}' missing for browser '{browser}'"
    
    @pytest.mark.parametrize("platform_name,expected_method", [
        (PlatformUtils.WINDOWS, "_get_windows_browser_paths"),
        (PlatformUtils.MACOS, "_get_macos_browser_paths"),
        (PlatformUtils.LINUX, "_get_linux_browser_paths"),
    ])
    def test_platform_method_routing(self, platform_name, expected_method):
        """Test that correct platform-specific method is called."""
        with patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_platform') as mock_platform:
            mock_platform.return_value = platform_name
            
            with patch.object(DataLocations, expected_method) as mock_method:
                mock_method.return_value = {}
                DataLocations.get_browser_data_paths("chrome")
                mock_method.assert_called_once_with("chrome")


class TestExecutionReporting:
    """Test execution reporting and metrics collection."""
    
    @classmethod
    def setup_class(cls):
        """Setup class-level test data."""
        cls.execution_start = datetime.now()
        cls.test_results = []
    
    @classmethod
    def teardown_class(cls):
        """Generate test execution report."""
        cls.execution_end = datetime.now()
        cls.total_duration = cls.execution_end - cls.execution_start
        
        # Create execution summary
        report = {
            "execution_timestamp": cls.execution_start.isoformat(),
            "completion_timestamp": cls.execution_end.isoformat(),
            "total_duration_seconds": cls.total_duration.total_seconds(),
            "test_module": "test_data_locations_2025-08-30.py",
            "target_module": "data_locations.py",
            "platform": platform.system(),
            "python_version": sys.version,
            "pytest_version": pytest.__version__,
        }
        
        # Write execution report
        report_path = Path(__file__).parent / "result_data_locations_2025-08-30_execution.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
    
    def test_reporting_setup(self):
        """Test that reporting infrastructure is working."""
        assert hasattr(self, '__class__')
        assert hasattr(self.__class__, 'execution_start')
        assert isinstance(self.__class__.execution_start, datetime)


# Fixtures for test data and mocking
@pytest.fixture
def mock_windows_environment():
    """Fixture providing mocked Windows environment."""
    with patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_platform') as mock_platform, \
         patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory') as mock_home, \
         patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_appdata_directory') as mock_appdata, \
         patch('utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_local_appdata_directory') as mock_local:
        
        mock_platform.return_value = PlatformUtils.WINDOWS
        mock_home.return_value = Path("C:/Users/TestUser")
        mock_appdata.return_value = Path("C:/Users/TestUser/AppData/Roaming")
        mock_local.return_value = Path("C:/Users/TestUser/AppData/Local")
        
        yield {
            'platform': mock_platform,
            'home': mock_home,
            'appdata': mock_appdata,
            'local_appdata': mock_local
        }


@pytest.fixture
def sample_browser_data():
    """Fixture providing sample browser data for testing."""
    return {
        "chrome": {
            "profiles": [Path("C:/Users/Test/AppData/Local/Google/Chrome/User Data/Default")],
            "cookies": [Path("C:/Users/Test/AppData/Local/Google/Chrome/User Data/Default/Cookies")],
            "history": [Path("C:/Users/Test/AppData/Local/Google/Chrome/User Data/Default/History")],
        },
        "firefox": {
            "profiles": [Path("C:/Users/Test/AppData/Roaming/Mozilla/Firefox/Profiles/test.default")],
            "cookies": [Path("C:/Users/Test/AppData/Roaming/Mozilla/Firefox/Profiles/test.default/cookies.sqlite")],
            "history": [Path("C:/Users/Test/AppData/Roaming/Mozilla/Firefox/Profiles/test.default/places.sqlite")],
        }
    }


# Test configuration and markers
pytestmark = [
    pytest.mark.unit,
    pytest.mark.privacy_tools,
    pytest.mark.data_locations
]


if __name__ == "__main__":
    # Run tests with coverage and reporting
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--html=result_data_locations_2025-08-30.html",
        "--json-report",
        "--json-report-file=result_data_locations_2025-08-30.json",
        "--cov=utilities.privacy.privacy_tools.core.data_locations",
        "--cov-report=html:result_data_locations_2025-08-30_coverage",
        "--cov-report=json:result_data_locations_2025-08-30_coverage.json"
    ])