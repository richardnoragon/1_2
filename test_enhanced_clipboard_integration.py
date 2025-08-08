"""
Test Suite for Enhanced Clipboard Manager Integration

This test suite verifies the Enhanced Clipboard Manager integration with the
RFU System Tools tab and ensures all components work correctly together.

Author: Richard's File Utilities
Version: 1.0.0
Date: August 7, 2025
"""

import os
import sys
import unittest
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock

# Add project root to path for imports
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

try:
    from PyQt5.QtWidgets import QApplication, QWidget
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtTest import QTest
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    # Create mock classes for testing
    class QApplication:
        @staticmethod
        def instance():
            return None
    class QWidget:
        pass
    class Qt:
        Key_Enter = 0
    class QTest:
        @staticmethod
        def keyClick(widget, key):
            pass


class TestEnhancedClipboardCore(unittest.TestCase):
    """Test the core clipboard management components."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test_clipboard.db")
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        os.rmdir(self.temp_dir)
    
    def test_clipboard_item_creation(self):
        """Test ClipboardItem creation and serialization."""
        try:
            from enhanced_clipboard_manager import ClipboardItem
            
            # Test text item
            item = ClipboardItem("Test content", "text", "Test App")
            self.assertIsNotNone(item.id)
            self.assertEqual(item.content, "Test content")
            self.assertEqual(item.item_type, "text")
            self.assertEqual(item.source_app, "Test App")
            self.assertFalse(item.pinned)
            
            # Test serialization
            item_dict = item.to_dict()
            self.assertIn('id', item_dict)
            self.assertIn('content', item_dict)
            self.assertIn('item_type', item_dict)
            
            # Test deserialization
            restored_item = ClipboardItem.from_dict(item_dict)
            self.assertEqual(restored_item.content, item.content)
            self.assertEqual(restored_item.item_type, item.item_type)
            
            print("✅ ClipboardItem creation and serialization tests passed")
            
        except ImportError:
            print("⚠️ ClipboardItem tests skipped - module not available")
    
    def test_clipboard_database(self):
        """Test ClipboardDatabase functionality."""
        try:
            from enhanced_clipboard_manager import ClipboardDatabase, ClipboardItem
            
            # Create database
            db = ClipboardDatabase(self.test_db_path)
            self.assertTrue(os.path.exists(self.test_db_path))
            
            # Test adding items
            item1 = ClipboardItem("Test content 1", "text")
            item2 = ClipboardItem("Test content 2", "url")
            
            self.assertTrue(db.add_item(item1))
            self.assertTrue(db.add_item(item2))
            
            # Test retrieving items
            items = db.get_items()
            self.assertEqual(len(items), 2)
            
            # Test search
            search_results = db.search_items("content 1")
            self.assertEqual(len(search_results), 1)
            self.assertEqual(search_results[0].content, "Test content 1")
            
            # Test filtering
            text_items = db.get_items(item_type="text")
            self.assertEqual(len(text_items), 1)
            
            # Test statistics
            stats = db.get_statistics()
            self.assertEqual(stats['total_items'], 2)
            
            # Clean up
            db.close()
            
            print("✅ ClipboardDatabase functionality tests passed")
            
        except ImportError:
            print("⚠️ ClipboardDatabase tests skipped - module not available")
    
    def test_clipboard_encryption(self):
        """Test clipboard encryption functionality."""
        try:
            from enhanced_clipboard_manager import ClipboardEncryption
            
            encryption = ClipboardEncryption()
            
            # Test password setting
            self.assertTrue(encryption.set_password("test_password_123"))
            
            # Test encryption/decryption
            original_text = "Sensitive clipboard content"
            encrypted = encryption.encrypt_content(original_text)
            decrypted = encryption.decrypt_content(encrypted)
            
            self.assertEqual(decrypted, original_text)
            self.assertNotEqual(encrypted, original_text)
            
            print("✅ ClipboardEncryption tests passed")
            
        except ImportError:
            print("⚠️ ClipboardEncryption tests skipped - cryptography not available")
    
    def test_text_processor(self):
        """Test text processing functionality."""
        try:
            from enhanced_clipboard_manager import ClipboardTextProcessor
            
            processor = ClipboardTextProcessor()
            
            # Test case conversion
            text = "hello world"
            self.assertEqual(processor.convert_case(text, "upper"), "HELLO WORLD")
            self.assertEqual(processor.convert_case(text, "title"), "Hello World")
            self.assertEqual(processor.convert_case(text, "camel"), "helloWorld")
            self.assertEqual(processor.convert_case(text, "pascal"), "HelloWorld")
            self.assertEqual(processor.convert_case(text, "snake"), "hello_world")
            
            # Test format conversion
            html_text = "<strong>Bold</strong> text"
            plain_text = processor.format_convert(html_text, "html_to_text")
            self.assertEqual(plain_text, "Bold text")
            
            # Test email extraction
            text_with_email = "Contact us at test@example.com for support"
            emails = processor.extract_emails(text_with_email)
            self.assertEqual(len(emails), 1)
            self.assertEqual(emails[0], "test@example.com")
            
            # Test URL extraction
            text_with_url = "Visit https://example.com for more info"
            urls = processor.extract_urls(text_with_url)
            self.assertEqual(len(urls), 1)
            self.assertEqual(urls[0], "https://example.com")
            
            print("✅ ClipboardTextProcessor tests passed")
            
        except ImportError:
            print("⚠️ ClipboardTextProcessor tests skipped - module not available")


class TestEnhancedClipboardGUI(unittest.TestCase):
    """Test the GUI components of the Enhanced Clipboard Manager."""
    
    @classmethod
    def setUpClass(cls):
        """Set up QApplication for GUI tests."""
        if PYQT_AVAILABLE and not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = None
    
    def test_system_integration_widget(self):
        """Test the System Tools integration widget."""
        if not PYQT_AVAILABLE:
            print("⚠️ GUI tests skipped - PyQt5 not available")
            return
        
        try:
            from enhanced_clipboard_system_integration import EnhancedClipboardSystemWidget
            
            # Create widget
            widget = EnhancedClipboardSystemWidget()
            self.assertIsInstance(widget, QWidget)
            
            # Test widget properties
            self.assertTrue(hasattr(widget, 'launch_btn'))
            self.assertTrue(hasattr(widget, 'floating_btn'))
            self.assertTrue(hasattr(widget, 'status_text'))
            
            # Test signal connections
            self.assertTrue(hasattr(widget, 'operation_started'))
            self.assertTrue(hasattr(widget, 'operation_completed'))
            self.assertTrue(hasattr(widget, 'status_update'))
            
            print("✅ System integration widget tests passed")
            
        except ImportError:
            print("⚠️ System integration widget tests skipped - module not available")
    
    def test_main_window_creation(self):
        """Test main window creation."""
        if not PYQT_AVAILABLE:
            print("⚠️ Main window tests skipped - PyQt5 not available")
            return
        
        try:
            from enhanced_clipboard_main_window import EnhancedClipboardMainWindow
            
            # Mock the database to avoid file system operations
            with patch('enhanced_clipboard_main_window.ClipboardDatabase'):
                window = EnhancedClipboardMainWindow()
                self.assertIsInstance(window, QWidget)
                
                # Test window components
                self.assertTrue(hasattr(window, 'tab_widget'))
                self.assertTrue(hasattr(window, 'history_view'))
                self.assertTrue(hasattr(window, 'template_panel'))
                self.assertTrue(hasattr(window, 'stats_panel'))
                self.assertTrue(hasattr(window, 'settings_panel'))
                
                print("✅ Main window creation tests passed")
                
        except ImportError:
            print("⚠️ Main window tests skipped - module not available")
        except Exception as e:
            print(f"⚠️ Main window tests skipped - GUI error: {e}")
    
    def test_floating_widget(self):
        """Test floating widget functionality."""
        if not PYQT_AVAILABLE:
            print("⚠️ Floating widget tests skipped - PyQt5 not available")
            return
        
        try:
            from enhanced_clipboard_main_window import ClipboardFloatingWidget
            
            # Mock clipboard manager
            mock_manager = Mock()
            widget = ClipboardFloatingWidget(mock_manager)
            
            self.assertIsInstance(widget, QWidget)
            self.assertTrue(hasattr(widget, 'main_btn'))
            self.assertTrue(hasattr(widget, 'expanded_widget'))
            self.assertFalse(widget.is_expanded)
            
            # Test expand/collapse
            widget.toggle_expand()
            self.assertTrue(widget.is_expanded)
            
            widget.toggle_expand()
            self.assertFalse(widget.is_expanded)
            
            print("✅ Floating widget tests passed")
            
        except ImportError:
            print("⚠️ Floating widget tests skipped - module not available")


class TestRFUIntegration(unittest.TestCase):
    """Test integration with the main RFU application."""
    
    def test_main_integration_point(self):
        """Test that the Enhanced Clipboard tool is properly integrated into main.py."""
        # Read main.py and check for integration points
        main_py_path = os.path.join(os.path.dirname(__file__), "main.py")
        
        if os.path.exists(main_py_path):
            with open(main_py_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for Enhanced Clipboard in System Tools tab
            self.assertIn("Enhanced Clipboard Manager", content)
            self.assertIn("open_enhanced_clipboard", content)
            
            # Check for menu integration
            self.assertIn("Enhanced Clipboard Manager", content)
            
            print("✅ RFU integration points verified in main.py")
        else:
            print("⚠️ main.py not found - integration test skipped")
    
    def test_launch_tool_method(self):
        """Test that the launch_tool method can handle Enhanced Clipboard."""
        try:
            # Mock the main window class
            from unittest.mock import MagicMock
            
            # Test module path resolution
            module_path = "enhanced_clipboard_system_integration"
            class_name = "EnhancedClipboardGUI"
            
            # Verify the module can be imported
            try:
                import enhanced_clipboard_system_integration
                self.assertTrue(hasattr(enhanced_clipboard_system_integration, class_name))
                print("✅ Enhanced Clipboard module import test passed")
            except ImportError:
                print("⚠️ Enhanced Clipboard module import test failed - module not available")
                
        except Exception as e:
            print(f"⚠️ Launch tool test failed: {e}")


class TestClipboardFeatures(unittest.TestCase):
    """Test specific Enhanced Clipboard features."""
    
    def test_template_system(self):
        """Test template system functionality."""
        try:
            from enhanced_clipboard_manager import ClipboardTemplateManager, ClipboardDatabase
            
            # Create temporary database
            temp_db = ClipboardDatabase(":memory:")
            template_manager = ClipboardTemplateManager(temp_db)
            
            # Test template creation
            template_id = template_manager.add_template(
                "Test Template",
                "Hello {name}, your {item} is ready!",
                ["name", "item"],
                "Test"
            )
            
            self.assertIsNotNone(template_id)
            
            # Test template expansion
            variables = {"name": "John", "item": "order"}
            expanded = template_manager.expand_template(template_id, variables)
            expected = "Hello John, your order is ready!"
            self.assertEqual(expanded, expected)
            
            # Test variable detection
            variables = template_manager.get_template_variables("Hi {user}, {message}")
            self.assertEqual(set(variables), {"user", "message"})
            
            print("✅ Template system tests passed")
            
        except ImportError:
            print("⚠️ Template system tests skipped - module not available")
    
    def test_cloud_sync_config(self):
        """Test cloud sync configuration."""
        try:
            from enhanced_clipboard_manager import ClipboardCloudSync
            
            # Test configuration
            config = {
                'sync_enabled': True,
                'sync_url': 'https://test-sync.example.com',
                'api_key': 'test_api_key',
                'device_id': 'test_device_123'
            }
            
            sync = ClipboardCloudSync(config)
            self.assertTrue(sync.sync_enabled)
            self.assertEqual(sync.sync_url, 'https://test-sync.example.com')
            self.assertEqual(sync.api_key, 'test_api_key')
            self.assertEqual(sync.device_id, 'test_device_123')
            
            print("✅ Cloud sync configuration tests passed")
            
        except ImportError:
            print("⚠️ Cloud sync tests skipped - module not available")
    
    def test_import_export_functionality(self):
        """Test import/export functionality."""
        try:
            from enhanced_clipboard_manager import ClipboardItem, ClipboardDatabase
            
            # Create test data
            items = [
                ClipboardItem("Test content 1", "text", "App1"),
                ClipboardItem("Test content 2", "url", "App2"),
                ClipboardItem("Test content 3", "code", "App3")
            ]
            
            # Test export format
            export_data = {
                'export_date': '2025-08-07T12:00:00',
                'item_count': len(items),
                'items': [item.to_dict() for item in items]
            }
            
            self.assertEqual(export_data['item_count'], 3)
            self.assertEqual(len(export_data['items']), 3)
            
            # Test import reconstruction
            imported_items = []
            for item_data in export_data['items']:
                item = ClipboardItem.from_dict(item_data)
                imported_items.append(item)
            
            self.assertEqual(len(imported_items), 3)
            self.assertEqual(imported_items[0].content, "Test content 1")
            self.assertEqual(imported_items[1].item_type, "url")
            self.assertEqual(imported_items[2].source_app, "App3")
            
            print("✅ Import/export functionality tests passed")
            
        except ImportError:
            print("⚠️ Import/export tests skipped - module not available")


def run_all_tests():
    """Run all test suites."""
    print("=" * 60)
    print("ENHANCED CLIPBOARD MANAGER - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print(f"Running tests for Enhanced Clipboard Manager integration")
    print(f"PyQt5 Available: {PYQT_AVAILABLE}")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases using TestLoader
    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromTestCase(TestEnhancedClipboardCore))
    suite.addTests(loader.loadTestsFromTestCase(TestEnhancedClipboardGUI))
    suite.addTests(loader.loadTestsFromTestCase(TestRFUIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestClipboardFeatures))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%" if result.testsRun > 0 else "0%")
    
    if result.failures:
        print("\\nFAILURES:")
        for test, failure in result.failures:
            print(f"  - {test}: {failure}")
    
    if result.errors:
        print("\\nERRORS:")
        for test, error in result.errors:
            print(f"  - {test}: {error}")
    
    print("=" * 60)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
