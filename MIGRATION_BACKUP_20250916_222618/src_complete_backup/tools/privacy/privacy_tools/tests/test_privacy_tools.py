"""
Comprehensive test suite for Privacy Tools module.

Tests all privacy tools functionality including cross-platform compatibility,
browser detection, and privacy operations.
"""

import unittest
import tempfile
import shutil
import sqlite3
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import privacy tools components
from privacy_tools.core.platform_utils import PlatformUtils
from privacy_tools.core.browser_detector import BrowserDetector
from privacy_tools.core.data_locations import DataLocations
from privacy_tools.tools.secure_empty_trash import SecureEmptyTrashTool
from privacy_tools.tools.delete_cookies import DeleteCookiesTool


class TestPlatformUtils(unittest.TestCase):
    """Test platform utility functions."""
    
    def test_platform_detection(self):
        """Test platform detection."""
        platform = PlatformUtils.get_platform()
        self.assertIn(platform, [
            PlatformUtils.WINDOWS,
            PlatformUtils.MACOS,
            PlatformUtils.LINUX
        ])
    
    def test_platform_checks(self):
        """Test platform-specific checks."""
        platform = PlatformUtils.get_platform()
        
        if platform == PlatformUtils.WINDOWS:
            self.assertTrue(PlatformUtils.is_windows())
            self.assertFalse(PlatformUtils.is_macos())
            self.assertFalse(PlatformUtils.is_linux())
        elif platform == PlatformUtils.MACOS:
            self.assertFalse(PlatformUtils.is_windows())
            self.assertTrue(PlatformUtils.is_macos())
            self.assertFalse(PlatformUtils.is_linux())
        elif platform == PlatformUtils.LINUX:
            self.assertFalse(PlatformUtils.is_windows())
            self.assertFalse(PlatformUtils.is_macos())
            self.assertTrue(PlatformUtils.is_linux())
    
    def test_home_directory(self):
        """Test home directory detection."""
        home = PlatformUtils.get_home_directory()
        self.assertIsInstance(home, Path)
        self.assertTrue(home.exists())
    
    def test_appdata_directory(self):
        """Test application data directory detection."""
        appdata = PlatformUtils.get_appdata_directory()
        if appdata:  # May be None on some platforms
            self.assertIsInstance(appdata, Path)
    
    def test_secure_delete_file(self):
        """Test secure file deletion."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"test content for secure deletion")
            tmp_path = Path(tmp.name)
        
        # Ensure file exists
        self.assertTrue(tmp_path.exists())
        
        # Securely delete it
        result = PlatformUtils.secure_delete_file(tmp_path, passes=1)
        
        # File should be deleted
        self.assertTrue(result)
        self.assertFalse(tmp_path.exists())
    
    def test_process_detection(self):
        """Test process detection functionality."""
        processes = PlatformUtils.get_running_processes()
        self.assertIsInstance(processes, list)
        
        # Test with a process that should exist (current Python process)
        python_running = PlatformUtils.is_process_running("python")
        # Note: This might be False if running in a different interpreter


class TestDataLocations(unittest.TestCase):
    """Test browser data location mappings."""
    
    def test_supported_browsers(self):
        """Test supported browser list."""
        browsers = DataLocations.get_all_supported_browsers()
        self.assertIsInstance(browsers, list)
        self.assertIn(DataLocations.CHROME, browsers)
        self.assertIn(DataLocations.FIREFOX, browsers)
        self.assertIn(DataLocations.EDGE, browsers)
    
    def test_browser_data_paths(self):
        """Test browser data path retrieval."""
        for browser in DataLocations.get_all_supported_browsers():
            paths = DataLocations.get_browser_data_paths(browser)
            self.assertIsInstance(paths, dict)
            
            # Check expected keys exist
            expected_keys = ['profiles', 'cookies', 'history', 'downloads']
            for key in expected_keys:
                if key in paths:
                    self.assertIsInstance(paths[key], list)
    
    def test_system_data_paths(self):
        """Test system data path retrieval."""
        paths = DataLocations.get_system_data_paths()
        self.assertIsInstance(paths, dict)
        
        # Should have some platform-specific paths
        self.assertGreater(len(paths), 0)
    
    def test_browser_executables(self):
        """Test browser executable name mappings."""
        executables = DataLocations.get_browser_executable_names()
        self.assertIsInstance(executables, dict)
        
        for browser, exe_list in executables.items():
            self.assertIsInstance(exe_list, list)
            self.assertGreater(len(exe_list), 0)


class TestBrowserDetector(unittest.TestCase):
    """Test browser detection functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = BrowserDetector()
    
    def test_browser_detection(self):
        """Test browser detection."""
        browsers = self.detector.detect_installed_browsers()
        self.assertIsInstance(browsers, list)
        
        # Each detected browser should be in supported list
        supported = DataLocations.get_all_supported_browsers()
        for browser in browsers:
            self.assertIn(browser, supported)
    
    def test_running_browsers(self):
        """Test running browser detection."""
        running = self.detector.get_running_browsers()
        self.assertIsInstance(running, list)
        
        # Each running browser should be in detected list
        detected = self.detector.detect_installed_browsers()
        for browser in running:
            self.assertIn(browser, detected)
    
    def test_browser_data_paths(self):
        """Test browser data path retrieval."""
        detected = self.detector.detect_installed_browsers()
        
        for browser in detected:
            paths = self.detector.get_browser_data_paths(browser)
            self.assertIsInstance(paths, dict)
    
    def test_browser_info(self):
        """Test comprehensive browser information."""
        detected = self.detector.detect_installed_browsers()
        
        for browser in detected:
            info = self.detector.get_browser_info(browser)
            self.assertIsInstance(info, dict)
            
            # Check required keys
            required_keys = ['name', 'installed', 'running', 'data_paths']
            for key in required_keys:
                self.assertIn(key, info)


class TestSecureEmptyTrashTool(unittest.TestCase):
    """Test secure empty trash functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tool = SecureEmptyTrashTool()
    
    def test_tool_properties(self):
        """Test basic tool properties."""
        self.assertEqual(self.tool.name, "Secure Empty Trash")
        self.assertIsInstance(self.tool.get_description(), str)
        self.assertIsInstance(self.tool.get_supported_platforms(), list)
        self.assertIsInstance(self.tool.is_supported(), bool)
    
    def test_preview_operation(self):
        """Test operation preview."""
        preview = self.tool.preview_operation(secure_delete=False)
        self.assertIsInstance(preview, dict)
        
        # Check expected keys
        expected_keys = ['platform', 'secure_delete', 'trash_items']
        for key in expected_keys:
            self.assertIn(key, preview)
    
    @patch('privacy_tools.core.platform_utils.PlatformUtils.empty_trash')
    def test_execute_operation_mock(self, mock_empty_trash):
        """Test operation execution with mocked platform calls."""
        mock_empty_trash.return_value = True
        
        result = self.tool.execute_operation(secure_delete=False)
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result.success, bool)
        self.assertIsInstance(result.message, str)


class TestDeleteCookiesTool(unittest.TestCase):
    """Test cookie deletion functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tool = DeleteCookiesTool()
        self.temp_dir = Path(tempfile.mkdtemp())
        
    def tearDown(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_tool_properties(self):
        """Test basic tool properties."""
        self.assertEqual(self.tool.name, "Delete Browser Cookies")
        self.assertIsInstance(self.tool.get_description(), str)
        self.assertIsInstance(self.tool.get_supported_platforms(), list)
        self.assertIsInstance(self.tool.is_supported(), bool)
    
    def test_preview_operation(self):
        """Test operation preview."""
        preview = self.tool.preview_operation(browsers=['chrome'])
        self.assertIsInstance(preview, dict)
        
        # Check expected keys
        expected_keys = ['browsers', 'estimated_cookies', 'browser_status']
        for key in expected_keys:
            self.assertIn(key, preview)
    
    def create_test_cookie_db(self, db_type='chrome'):
        """Create a test cookie database."""
        db_path = self.temp_dir / "test_cookies.db"
        
        with sqlite3.connect(str(db_path)) as conn:
            cursor = conn.cursor()
            
            if db_type == 'chrome':
                cursor.execute("""
                    CREATE TABLE cookies (
                        host_key TEXT,
                        name TEXT,
                        value TEXT,
                        creation_utc INTEGER,
                        expires_utc INTEGER
                    )
                """)
                
                # Insert test cookies
                test_cookies = [
                    ('google.com', 'test1', 'value1', 13000000000000000, 13000000000000000),
                    ('facebook.com', 'test2', 'value2', 13000000000000000, 13000000000000000),
                    ('example.com', 'test3', 'value3', 13000000000000000, 13000000000000000),
                ]
                
                cursor.executemany(
                    "INSERT INTO cookies VALUES (?, ?, ?, ?, ?)",
                    test_cookies
                )
                
            elif db_type == 'firefox':
                cursor.execute("""
                    CREATE TABLE moz_cookies (
                        host TEXT,
                        name TEXT,
                        value TEXT,
                        creationTime INTEGER,
                        expiry INTEGER
                    )
                """)
                
                # Insert test cookies
                test_cookies = [
                    ('google.com', 'test1', 'value1', 1600000000000000, 1600000000),
                    ('facebook.com', 'test2', 'value2', 1600000000000000, 1600000000),
                    ('example.com', 'test3', 'value3', 1600000000000000, 1600000000),
                ]
                
                cursor.executemany(
                    "INSERT INTO moz_cookies VALUES (?, ?, ?, ?, ?)",
                    test_cookies
                )
            
            conn.commit()
        
        return db_path
    
    def test_count_chromium_cookies(self):
        """Test Chromium cookie counting."""
        db_path = self.create_test_cookie_db('chrome')
        
        count = self.tool._count_chromium_cookies(db_path)
        self.assertEqual(count, 3)
        
        # Test with domain filter
        count_filtered = self.tool._count_chromium_cookies(
            db_path, domain_filter='google'
        )
        self.assertEqual(count_filtered, 1)
    
    def test_count_firefox_cookies(self):
        """Test Firefox cookie counting."""
        db_path = self.create_test_cookie_db('firefox')
        
        count = self.tool._count_firefox_cookies(db_path)
        self.assertEqual(count, 3)
        
        # Test with domain filter
        count_filtered = self.tool._count_firefox_cookies(
            db_path, domain_filter='google'
        )
        self.assertEqual(count_filtered, 1)
    
    def test_delete_chromium_cookies(self):
        """Test Chromium cookie deletion."""
        db_path = self.create_test_cookie_db('chrome')
        
        # Delete all cookies
        deleted = self.tool._delete_chromium_cookies(db_path)
        self.assertEqual(deleted, 3)
        
        # Verify deletion
        count_after = self.tool._count_chromium_cookies(db_path)
        self.assertEqual(count_after, 0)
    
    def test_delete_firefox_cookies(self):
        """Test Firefox cookie deletion."""
        db_path = self.create_test_cookie_db('firefox')
        
        # Delete all cookies
        deleted = self.tool._delete_firefox_cookies(db_path)
        self.assertEqual(deleted, 3)
        
        # Verify deletion
        count_after = self.tool._count_firefox_cookies(db_path)
        self.assertEqual(count_after, 0)


class TestPrivacyToolsIntegration(unittest.TestCase):
    """Integration tests for privacy tools."""
    
    def test_tool_instantiation(self):
        """Test that all tools can be instantiated."""
        tools = [
            SecureEmptyTrashTool(),
            DeleteCookiesTool()
        ]
        
        for tool in tools:
            self.assertIsNotNone(tool)
            self.assertIsInstance(tool.name, str)
            self.assertTrue(len(tool.name) > 0)
    
    def test_cross_platform_support(self):
        """Test cross-platform support claims."""
        tools = [
            SecureEmptyTrashTool(),
            DeleteCookiesTool()
        ]
        
        current_platform = PlatformUtils.get_platform()
        
        for tool in tools:
            supported_platforms = tool.get_supported_platforms()
            self.assertIsInstance(supported_platforms, list)
            
            # Current platform should be supported
            self.assertIn(current_platform, supported_platforms)
            
            # is_supported() should return True
            self.assertTrue(tool.is_supported())


def run_tests():
    """Run all privacy tools tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestPlatformUtils,
        TestDataLocations,
        TestBrowserDetector,
        TestSecureEmptyTrashTool,
        TestDeleteCookiesTool,
        TestPrivacyToolsIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)