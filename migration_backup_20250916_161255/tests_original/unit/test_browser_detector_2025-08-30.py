"""
Comprehensive unit tests for browser_detector.py
Test file: test_browser_detector_2025-08-30.py
Created: 2025-08-30
Target: src/utilities/privacy/privacy_tools/core/browser_detector.py

This module provides comprehensive testing coverage for the BrowserDetector class,
including all methods, edge cases, and error conditions with proper mocking.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Set
from unittest.mock import MagicMock, Mock, mock_open, patch

import pytest

# Add the source directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from src.utilities.privacy.privacy_tools.core.browser_detector import \
        BrowserDetector
    from src.utilities.privacy.privacy_tools.core.data_locations import \
        DataLocations
    from src.utilities.privacy.privacy_tools.core.platform_utils import \
        PlatformUtils
except ImportError as e:
    pytest.skip(f"Required modules not available: {e}", allow_module_level=True)


class TestBrowserDetector:
    """Test suite for BrowserDetector class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.detector = BrowserDetector()
        self.test_home = Path("/test/home")
        self.test_appdata = Path("/test/appdata")
        self.test_local_appdata = Path("/test/local_appdata")
    
    def teardown_method(self):
        """Clean up after each test method."""
        # Reset any cached data
        if hasattr(self.detector, '_detected_browsers'):
            self.detector._detected_browsers = None
        if hasattr(self.detector, '_browser_paths'):
            self.detector._browser_paths.clear()
    
    def test_init(self):
        """Test BrowserDetector initialization."""
        detector = BrowserDetector()
        assert detector._detected_browsers is None
        assert detector._browser_paths == {}
        assert hasattr(detector, 'platform')
    
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_platform')
    def test_init_platform_detection(self, mock_get_platform):
        """Test platform detection during initialization."""
        mock_get_platform.return_value = PlatformUtils.WINDOWS
        detector = BrowserDetector()
        assert detector.platform == PlatformUtils.WINDOWS
        mock_get_platform.assert_called_once()
    
    @patch.object(BrowserDetector, '_is_browser_installed')
    @patch('src.utilities.privacy.privacy_tools.core.data_locations.DataLocations.get_all_supported_browsers')
    def test_detect_installed_browsers_fresh(self, mock_get_browsers, mock_is_installed):
        """Test browser detection on fresh instance."""
        mock_get_browsers.return_value = ['chrome', 'firefox', 'edge']
        mock_is_installed.side_effect = [True, False, True]
        
        result = self.detector.detect_installed_browsers()
        
        assert result == ['chrome', 'edge']
        assert self.detector._detected_browsers == ['chrome', 'edge']
        assert mock_is_installed.call_count == 3
    
    def test_detect_installed_browsers_cached(self):
        """Test browser detection with cached results."""
        # Set cached result
        self.detector._detected_browsers = ['chrome', 'firefox']
        
        result = self.detector.detect_installed_browsers()
        
        assert result == ['chrome', 'firefox']
    
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_platform')
    def test_is_browser_installed_windows(self, mock_get_platform):
        """Test browser installation check on Windows."""
        mock_get_platform.return_value = PlatformUtils.WINDOWS
        self.detector.platform = PlatformUtils.WINDOWS
        
        with patch.object(self.detector, '_check_windows_browser') as mock_check:
            mock_check.return_value = True
            result = self.detector._is_browser_installed('chrome')
            
            assert result is True
            mock_check.assert_called_once_with('chrome')
    
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_platform')
    def test_is_browser_installed_macos(self, mock_get_platform):
        """Test browser installation check on macOS."""
        mock_get_platform.return_value = PlatformUtils.MACOS
        self.detector.platform = PlatformUtils.MACOS
        
        with patch.object(self.detector, '_check_macos_browser') as mock_check:
            mock_check.return_value = True
            result = self.detector._is_browser_installed('safari')
            
            assert result is True
            mock_check.assert_called_once_with('safari')
    
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_platform')
    def test_is_browser_installed_linux(self, mock_get_platform):
        """Test browser installation check on Linux."""
        mock_get_platform.return_value = PlatformUtils.LINUX
        self.detector.platform = PlatformUtils.LINUX
        
        with patch.object(self.detector, '_check_linux_browser') as mock_check:
            mock_check.return_value = True
            result = self.detector._is_browser_installed('firefox')
            
            assert result is True
            mock_check.assert_called_once_with('firefox')
    
    def test_is_browser_installed_unknown_platform(self):
        """Test browser installation check on unknown platform."""
        self.detector.platform = "unknown"
        result = self.detector._is_browser_installed('chrome')
        assert result is False
    
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory')
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_local_appdata_directory')
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_appdata_directory')
    def test_check_windows_browser_chrome_exists(self, mock_appdata, mock_local_appdata, mock_home):
        """Test Windows Chrome detection when installed."""
        mock_home.return_value = self.test_home
        mock_local_appdata.return_value = self.test_local_appdata
        mock_appdata.return_value = self.test_appdata
        
        chrome_path = self.test_local_appdata / "Google" / "Chrome"
        
        with patch.object(Path, 'exists') as mock_exists:
            mock_exists.return_value = True
            result = self.detector._check_windows_browser(DataLocations.CHROME)
            
            assert result is True
    
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory')
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_local_appdata_directory')
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_appdata_directory')
    def test_check_windows_browser_chrome_not_exists(self, mock_appdata, mock_local_appdata, mock_home):
        """Test Windows Chrome detection when not installed."""
        mock_home.return_value = self.test_home
        mock_local_appdata.return_value = self.test_local_appdata
        mock_appdata.return_value = self.test_appdata
        
        with patch.object(Path, 'exists') as mock_exists:
            mock_exists.return_value = False
            result = self.detector._check_windows_browser(DataLocations.CHROME)
            
            assert result is False
    
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory')
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_local_appdata_directory')
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_appdata_directory')
    def test_check_windows_browser_firefox_exists(self, mock_appdata, mock_local_appdata, mock_home):
        """Test Windows Firefox detection when installed."""
        mock_home.return_value = self.test_home
        mock_local_appdata.return_value = self.test_local_appdata
        mock_appdata.return_value = self.test_appdata
        
        with patch.object(Path, 'exists') as mock_exists:
            mock_exists.return_value = True
            result = self.detector._check_windows_browser(DataLocations.FIREFOX)
            
            assert result is True
    
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory')
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_local_appdata_directory')
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_appdata_directory')
    def test_check_windows_browser_edge_exists(self, mock_appdata, mock_local_appdata, mock_home):
        """Test Windows Edge detection when installed."""
        mock_home.return_value = self.test_home
        mock_local_appdata.return_value = self.test_local_appdata
        mock_appdata.return_value = self.test_appdata
        
        with patch.object(Path, 'exists') as mock_exists:
            mock_exists.return_value = True
            result = self.detector._check_windows_browser(DataLocations.EDGE)
            
            assert result is True
    
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory')
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_local_appdata_directory')
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_appdata_directory')
    def test_check_windows_browser_no_appdata(self, mock_appdata, mock_local_appdata, mock_home):
        """Test Windows browser detection when appdata directories are None."""
        mock_home.return_value = self.test_home
        mock_local_appdata.return_value = None
        mock_appdata.return_value = None
        
        result = self.detector._check_windows_browser(DataLocations.CHROME)
        assert result is False
    
    def test_check_windows_browser_unknown_browser(self):
        """Test Windows browser detection for unknown browser."""
        result = self.detector._check_windows_browser("unknown_browser")
        assert result is False
    
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory')
    def test_check_macos_browser_chrome_exists(self, mock_home):
        """Test macOS Chrome detection when installed."""
        mock_home.return_value = self.test_home
        
        with patch.object(Path, 'exists') as mock_exists:
            mock_exists.return_value = True
            result = self.detector._check_macos_browser(DataLocations.CHROME)
            
            assert result is True
    
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory')
    def test_check_macos_browser_firefox_exists(self, mock_home):
        """Test macOS Firefox detection when installed."""
        mock_home.return_value = self.test_home
        
        with patch.object(Path, 'exists') as mock_exists:
            mock_exists.return_value = True
            result = self.detector._check_macos_browser(DataLocations.FIREFOX)
            
            assert result is True
    
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory')
    def test_check_macos_browser_safari_exists(self, mock_home):
        """Test macOS Safari detection when installed."""
        mock_home.return_value = self.test_home
        
        with patch.object(Path, 'exists') as mock_exists:
            mock_exists.return_value = True
            result = self.detector._check_macos_browser(DataLocations.SAFARI)
            
            assert result is True
    
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory')
    def test_check_macos_browser_edge_exists(self, mock_home):
        """Test macOS Edge detection when installed."""
        mock_home.return_value = self.test_home
        
        with patch.object(Path, 'exists') as mock_exists:
            mock_exists.return_value = True
            result = self.detector._check_macos_browser(DataLocations.EDGE)
            
            assert result is True
    
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory')
    def test_check_macos_browser_not_exists(self, mock_home):
        """Test macOS browser detection when not installed."""
        mock_home.return_value = self.test_home
        
        with patch.object(Path, 'exists') as mock_exists:
            mock_exists.return_value = False
            result = self.detector._check_macos_browser(DataLocations.CHROME)
            
            assert result is False
    
    def test_check_macos_browser_unknown_browser(self):
        """Test macOS browser detection for unknown browser."""
        result = self.detector._check_macos_browser("unknown_browser")
        assert result is False
    
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory')
    def test_check_linux_browser_chrome_config_exists(self, mock_home):
        """Test Linux Chrome detection when config directory exists."""
        mock_home.return_value = self.test_home
        
        with patch.object(Path, 'exists') as mock_exists:
            mock_exists.return_value = True
            result = self.detector._check_linux_browser(DataLocations.CHROME)
            
            assert result is True
    
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory')
    @patch.object(BrowserDetector, '_check_command_exists')
    def test_check_linux_browser_chrome_command_exists(self, mock_command_exists, mock_home):
        """Test Linux Chrome detection when command exists."""
        mock_home.return_value = self.test_home
        mock_command_exists.return_value = True
        
        with patch.object(Path, 'exists') as mock_exists:
            mock_exists.return_value = False
            result = self.detector._check_linux_browser(DataLocations.CHROME)
            
            assert result is True
            mock_command_exists.assert_called_once_with("google-chrome")
    
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory')
    def test_check_linux_browser_firefox_exists(self, mock_home):
        """Test Linux Firefox detection when installed."""
        mock_home.return_value = self.test_home
        
        with patch.object(Path, 'exists') as mock_exists:
            mock_exists.return_value = True
            result = self.detector._check_linux_browser(DataLocations.FIREFOX)
            
            assert result is True
    
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory')
    def test_check_linux_browser_edge_exists(self, mock_home):
        """Test Linux Edge detection when installed."""
        mock_home.return_value = self.test_home
        
        with patch.object(Path, 'exists') as mock_exists:
            mock_exists.return_value = True
            result = self.detector._check_linux_browser(DataLocations.EDGE)
            
            assert result is True
    
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory')
    @patch.object(BrowserDetector, '_check_command_exists')
    def test_check_linux_browser_not_exists(self, mock_command_exists, mock_home):
        """Test Linux browser detection when not installed."""
        mock_home.return_value = self.test_home
        mock_command_exists.return_value = False
        
        with patch.object(Path, 'exists') as mock_exists:
            mock_exists.return_value = False
            result = self.detector._check_linux_browser(DataLocations.CHROME)
            
            assert result is False
    
    def test_check_linux_browser_unknown_browser(self):
        """Test Linux browser detection for unknown browser."""
        result = self.detector._check_linux_browser("unknown_browser")
        assert result is False
    
    @patch('shutil.which')
    def test_check_command_exists_found(self, mock_which):
        """Test command existence check when command is found."""
        mock_which.return_value = "/usr/bin/firefox"
        result = self.detector._check_command_exists("firefox")
        
        assert result is True
        mock_which.assert_called_once_with("firefox")
    
    @patch('shutil.which')
    def test_check_command_exists_not_found(self, mock_which):
        """Test command existence check when command is not found."""
        mock_which.return_value = None
        result = self.detector._check_command_exists("nonexistent_command")
        
        assert result is False
        mock_which.assert_called_once_with("nonexistent_command")
    
    @patch.object(BrowserDetector, 'detect_installed_browsers')
    @patch('src.utilities.privacy.privacy_tools.core.data_locations.DataLocations.get_browser_executable_names')
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.is_process_running')
    def test_get_running_browsers(self, mock_is_running, mock_get_exes, mock_detect):
        """Test getting list of running browsers."""
        mock_detect.return_value = ['chrome', 'firefox']
        mock_get_exes.return_value = {
            'chrome': ['chrome.exe', 'google-chrome'],
            'firefox': ['firefox.exe', 'firefox']
        }
        mock_is_running.side_effect = [True, False, False, True]
        
        result = self.detector.get_running_browsers()
        
        assert result == ['chrome', 'firefox']
        assert mock_is_running.call_count == 4
    
    @patch.object(BrowserDetector, 'get_running_browsers')
    def test_is_browser_running_true(self, mock_get_running):
        """Test checking if specific browser is running - true case."""
        mock_get_running.return_value = ['chrome', 'firefox']
        
        result = self.detector.is_browser_running('chrome')
        assert result is True
    
    @patch.object(BrowserDetector, 'get_running_browsers')
    def test_is_browser_running_false(self, mock_get_running):
        """Test checking if specific browser is running - false case."""
        mock_get_running.return_value = ['firefox']
        
        result = self.detector.is_browser_running('chrome')
        assert result is False
    
    @patch.object(BrowserDetector, 'is_browser_running')
    def test_close_browser_not_running(self, mock_is_running):
        """Test closing browser when it's not running."""
        mock_is_running.return_value = False
        
        result = self.detector.close_browser('chrome')
        assert result is True
    
    @patch.object(BrowserDetector, 'is_browser_running')
    @patch('src.utilities.privacy.privacy_tools.core.data_locations.DataLocations.get_browser_executable_names')
    def test_close_browser_unknown_browser(self, mock_get_exes, mock_is_running):
        """Test closing unknown browser."""
        mock_is_running.return_value = True
        mock_get_exes.return_value = {}
        
        result = self.detector.close_browser('unknown_browser')
        assert result is False
    
    @patch.object(BrowserDetector, 'is_browser_running')
    @patch('src.utilities.privacy.privacy_tools.core.data_locations.DataLocations.get_browser_executable_names')
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.is_process_running')
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.kill_process')
    def test_close_browser_success(self, mock_kill, mock_is_running_process, mock_get_exes, mock_is_running):
        """Test successfully closing a running browser."""
        mock_is_running.return_value = True
        mock_get_exes.return_value = {'chrome': ['chrome.exe']}
        mock_is_running_process.return_value = True
        mock_kill.return_value = True
        
        result = self.detector.close_browser('chrome')
        
        assert result is True
        mock_kill.assert_called_once_with('chrome.exe')
    
    @patch.object(BrowserDetector, 'is_browser_running')
    @patch('src.utilities.privacy.privacy_tools.core.data_locations.DataLocations.get_browser_executable_names')
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.is_process_running')
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.kill_process')
    def test_close_browser_failure(self, mock_kill, mock_is_running_process, mock_get_exes, mock_is_running):
        """Test failing to close a running browser."""
        mock_is_running.return_value = True
        mock_get_exes.return_value = {'chrome': ['chrome.exe']}
        mock_is_running_process.return_value = True
        mock_kill.return_value = False
        
        result = self.detector.close_browser('chrome')
        
        assert result is False
        mock_kill.assert_called_once_with('chrome.exe')
    
    @patch('src.utilities.privacy.privacy_tools.core.data_locations.DataLocations.get_browser_data_paths')
    def test_get_browser_data_paths_fresh(self, mock_get_paths):
        """Test getting browser data paths for first time."""
        expected_paths = {
            'profiles': [Path('/test/profile1')],
            'cookies': [Path('/test/cookies')]
        }
        mock_get_paths.return_value = expected_paths
        
        result = self.detector.get_browser_data_paths('chrome')
        
        assert result == expected_paths
        assert self.detector._browser_paths['chrome'] == expected_paths
        mock_get_paths.assert_called_once_with('chrome')
    
    def test_get_browser_data_paths_cached(self):
        """Test getting browser data paths from cache."""
        cached_paths = {
            'profiles': [Path('/cached/profile')],
            'history': [Path('/cached/history')]
        }
        self.detector._browser_paths['firefox'] = cached_paths
        
        result = self.detector.get_browser_data_paths('firefox')
        
        assert result == cached_paths
    
    @patch.object(BrowserDetector, 'get_browser_data_paths')
    def test_get_browser_profile_paths(self, mock_get_data_paths):
        """Test getting browser profile paths."""
        mock_get_data_paths.return_value = {
            'profiles': [Path('/test/profile1'), Path('/test/profile2')],
            'cookies': [Path('/test/cookies')]
        }
        
        result = self.detector.get_browser_profile_paths('chrome')
        
        assert result == [Path('/test/profile1'), Path('/test/profile2')]
        mock_get_data_paths.assert_called_once_with('chrome')
    
    @patch.object(BrowserDetector, 'get_browser_data_paths')
    def test_get_browser_profile_paths_no_profiles(self, mock_get_data_paths):
        """Test getting browser profile paths when no profiles key exists."""
        mock_get_data_paths.return_value = {
            'cookies': [Path('/test/cookies')]
        }
        
        result = self.detector.get_browser_profile_paths('chrome')
        
        assert result == []
    
    @patch.object(BrowserDetector, 'get_browser_data_paths')
    def test_validate_browser_access_all_accessible(self, mock_get_data_paths):
        """Test browser access validation when all paths are accessible."""
        test_file = Path('/test/cookies')
        test_dir = Path('/test/profiles')
        
        mock_get_data_paths.return_value = {
            'cookies': [test_file],
            'profiles': [test_dir]
        }
        
        with patch.object(Path, 'exists') as mock_exists, \
             patch.object(Path, 'is_file') as mock_is_file, \
             patch.object(Path, 'is_dir') as mock_is_dir, \
             patch('builtins.open', mock_open(read_data=b'test')), \
             patch.object(Path, 'iterdir') as mock_iterdir:
            
            mock_exists.return_value = True
            mock_is_file.return_value = True
            mock_is_dir.return_value = True
            mock_iterdir.return_value = []
            
            result = self.detector.validate_browser_access('chrome')
            
            assert result == {'cookies': True, 'profiles': True}
    
    @patch.object(BrowserDetector, 'get_browser_data_paths')
    def test_validate_browser_access_permission_error(self, mock_get_data_paths):
        """Test browser access validation with permission errors."""
        test_file = Path('/test/cookies')
        
        mock_get_data_paths.return_value = {
            'cookies': [test_file]
        }
        
        with patch.object(Path, 'exists') as mock_exists, \
             patch.object(Path, 'is_file') as mock_is_file, \
             patch('builtins.open') as mock_open_file:
            
            mock_exists.return_value = True
            mock_is_file.return_value = True
            mock_open_file.side_effect = PermissionError("Access denied")
            
            result = self.detector.validate_browser_access('chrome')
            
            assert result == {'cookies': False}
    
    @patch.object(BrowserDetector, 'get_browser_data_paths')
    def test_validate_browser_access_file_not_exists(self, mock_get_data_paths):
        """Test browser access validation when files don't exist."""
        test_file = Path('/test/nonexistent')
        
        mock_get_data_paths.return_value = {
            'cookies': [test_file]
        }
        
        with patch.object(Path, 'exists') as mock_exists:
            mock_exists.return_value = False
            
            result = self.detector.validate_browser_access('chrome')
            
            assert result == {'cookies': True}  # Non-existent files are considered accessible
    
    @patch.object(BrowserDetector, 'detect_installed_browsers')
    @patch.object(BrowserDetector, 'is_browser_running')
    @patch.object(BrowserDetector, 'get_browser_data_paths')
    @patch.object(BrowserDetector, 'validate_browser_access')
    def test_get_browser_info(self, mock_validate, mock_get_paths, mock_is_running, mock_detect):
        """Test getting comprehensive browser information."""
        mock_detect.return_value = ['chrome', 'firefox']
        mock_is_running.return_value = True
        mock_get_paths.return_value = {'profiles': [Path('/test/profile')]}
        mock_validate.return_value = {'profiles': True}
        
        result = self.detector.get_browser_info('chrome')
        
        expected = {
            'name': 'chrome',
            'installed': True,
            'running': True,
            'data_paths': {'profiles': [Path('/test/profile')]},
            'access_status': {'profiles': True}
        }
        
        assert result == expected
    
    @patch.object(BrowserDetector, 'detect_installed_browsers')
    @patch.object(BrowserDetector, 'get_browser_info')
    def test_get_all_browser_info(self, mock_get_info, mock_detect):
        """Test getting information for all detected browsers."""
        mock_detect.return_value = ['chrome', 'firefox']
        mock_get_info.side_effect = [
            {'name': 'chrome', 'installed': True, 'running': False},
            {'name': 'firefox', 'installed': True, 'running': True}
        ]
        
        result = self.detector.get_all_browser_info()
        
        expected = {
            'chrome': {'name': 'chrome', 'installed': True, 'running': False},
            'firefox': {'name': 'firefox', 'installed': True, 'running': True}
        }
        
        assert result == expected
        assert mock_get_info.call_count == 2
    
    def test_refresh_detection(self):
        """Test refreshing browser detection cache."""
        # Set some cached data
        self.detector._detected_browsers = ['chrome']
        self.detector._browser_paths = {'chrome': {'profiles': []}}
        
        self.detector.refresh_detection()
        
        assert self.detector._detected_browsers is None
        assert self.detector._browser_paths == {}


class TestBrowserDetectorEdgeCases:
    """Test suite for edge cases and error conditions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = BrowserDetector()
    
    @patch('src.utilities.privacy.privacy_tools.core.data_locations.DataLocations.get_all_supported_browsers')
    def test_detect_browsers_empty_list(self, mock_get_browsers):
        """Test detection when no browsers are supported."""
        mock_get_browsers.return_value = []
        
        result = self.detector.detect_installed_browsers()
        assert result == []
    
    @patch.object(BrowserDetector, '_is_browser_installed')
    @patch('src.utilities.privacy.privacy_tools.core.data_locations.DataLocations.get_all_supported_browsers')
    def test_detect_browsers_all_not_installed(self, mock_get_browsers, mock_is_installed):
        """Test detection when no browsers are installed."""
        mock_get_browsers.return_value = ['chrome', 'firefox']
        mock_is_installed.return_value = False
        
        result = self.detector.detect_installed_browsers()
        assert result == []
    
    @patch.object(BrowserDetector, 'detect_installed_browsers')
    @patch('src.utilities.privacy.privacy_tools.core.data_locations.DataLocations.get_browser_executable_names')
    def test_get_running_browsers_no_executables(self, mock_get_exes, mock_detect):
        """Test getting running browsers when no executable info available."""
        mock_detect.return_value = ['chrome']
        mock_get_exes.return_value = {}
        
        result = self.detector.get_running_browsers()
        assert result == []
    
    @patch.object(BrowserDetector, 'get_browser_data_paths')
    def test_validate_access_empty_paths(self, mock_get_paths):
        """Test access validation with empty data paths."""
        mock_get_paths.return_value = {}
        
        result = self.detector.validate_browser_access('chrome')
        assert result == {}
    
    @patch.object(BrowserDetector, 'get_browser_data_paths')
    def test_validate_access_os_error(self, mock_get_paths):
        """Test access validation with OS errors."""
        test_file = Path('/test/locked_file')
        mock_get_paths.return_value = {'cookies': [test_file]}
        
        with patch.object(Path, 'exists') as mock_exists, \
             patch.object(Path, 'is_file') as mock_is_file, \
             patch('builtins.open') as mock_open_file:
            
            mock_exists.return_value = True
            mock_is_file.return_value = True
            mock_open_file.side_effect = OSError("System error")
            
            result = self.detector.validate_browser_access('chrome')
            assert result == {'cookies': False}


class TestBrowserDetectorParameterized:
    """Parameterized tests for multiple browser types and platforms."""
    
    @pytest.mark.parametrize("browser", [
        DataLocations.CHROME,
        DataLocations.FIREFOX,
        DataLocations.EDGE
    ])
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory')
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_local_appdata_directory')
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_appdata_directory')
    def test_windows_browser_detection_all_browsers(self, mock_appdata, mock_local_appdata, 
                                                   mock_home, browser):
        """Test Windows browser detection for all supported browsers."""
        detector = BrowserDetector()
        mock_home.return_value = Path("/test/home")
        mock_local_appdata.return_value = Path("/test/local_appdata")
        mock_appdata.return_value = Path("/test/appdata")
        
        with patch.object(Path, 'exists') as mock_exists:
            mock_exists.return_value = True
            result = detector._check_windows_browser(browser)
            assert result is True
    
    @pytest.mark.parametrize("platform,method", [
        (PlatformUtils.WINDOWS, '_check_windows_browser'),
        (PlatformUtils.MACOS, '_check_macos_browser'),
        (PlatformUtils.LINUX, '_check_linux_browser')
    ])
    def test_platform_specific_methods(self, platform, method):
        """Test that correct platform-specific methods are called."""
        detector = BrowserDetector()
        detector.platform = platform
        
        with patch.object(detector, method) as mock_method:
            mock_method.return_value = True
            result = detector._is_browser_installed('chrome')
            
            assert result is True
            mock_method.assert_called_once_with('chrome')
    
    @pytest.mark.parametrize("exists_results,expected", [
        ([True, True], True),   # Both application and data paths exist
        ([True, False], True),  # Only application path exists
        ([False, True], True),  # Only data path exists
        ([False, False], False) # Neither exists
    ])
    @patch('src.utilities.privacy.privacy_tools.core.platform_utils.PlatformUtils.get_home_directory')
    def test_macos_chrome_detection_combinations(self, mock_home, exists_results, expected):
        """Test macOS Chrome detection with different path combinations."""
        detector = BrowserDetector()
        mock_home.return_value = Path("/test/home")
        
        with patch.object(Path, 'exists') as mock_exists:
            mock_exists.side_effect = exists_results
            result = detector._check_macos_browser(DataLocations.CHROME)
            
            assert result == expected


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])