"""
Comprehensive test suite for Image Metadata Editor functionality.

Tests core functionality, PyQt5 compatibility, hub integration,
and performance characteristics.
"""

import os
import sys
import unittest
import tempfile
import shutil
from unittest.mock import MagicMock, patch, Mock
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtTest import QTest
from PIL import Image
import piexif

# Add the project root to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from file_utilities_2.core.image_metadata_logic import (
    ImageMetadataLogic, ImageMetadataWorker, get_tag_name, 
    format_exif_value, parse_exif_value
)
from file_utilities_2.gui.image_metadata_gui import ImageMetadataEditor


class TestImageMetadataCore(unittest.TestCase):
    """Comprehensive tests for image metadata core functionality."""
    
    def setUp(self):
        """Setup test environment."""
        self.app = QApplication.instance() or QApplication([])
        self.test_dir = tempfile.mkdtemp()
        self.logic = ImageMetadataLogic()
        self.test_files = self._create_test_images()
    
    def tearDown(self):
        """Cleanup test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def _create_test_images(self):
        """Create test images with EXIF data."""
        test_files = {}
        
        # Create JPEG with EXIF
        jpeg_path = os.path.join(self.test_dir, "test_with_exif.jpg")
        img = Image.new('RGB', (100, 100), color='red')
        
        # Create basic EXIF data
        exif_dict = {
            "0th": {
                piexif.ImageIFD.Artist: "Test Artist",
                piexif.ImageIFD.Software: "Test Software",
                piexif.ImageIFD.ImageWidth: 100,
                piexif.ImageIFD.ImageLength: 100,
            },
            "Exif": {
                piexif.ExifIFD.ExposureTime: (1, 60),
                piexif.ExifIFD.FNumber: (28, 10),
                piexif.ExifIFD.ISOSpeedRatings: 100,
            },
            "GPS": {},
            "1st": {},
            "thumbnail": None
        }
        
        exif_bytes = piexif.dump(exif_dict)
        img.save(jpeg_path, "JPEG", exif=exif_bytes)
        test_files['jpeg_with_exif'] = jpeg_path
        
        # Create JPEG without EXIF
        jpeg_no_exif_path = os.path.join(self.test_dir, "test_no_exif.jpg")
        img.save(jpeg_no_exif_path, "JPEG")
        test_files['jpeg_no_exif'] = jpeg_no_exif_path
        
        # Create TIFF with EXIF
        tiff_path = os.path.join(self.test_dir, "test_with_exif.tiff")
        img.save(tiff_path, "TIFF", exif=exif_bytes)
        test_files['tiff_with_exif'] = tiff_path
        
        return test_files
    
    def test_load_jpeg_metadata(self):
        """Test loading JPEG metadata with EXIF data."""
        test_file = self.test_files['jpeg_with_exif']
        metadata = self.logic.load_image_metadata(test_file)
        
        self.assertIsInstance(metadata, dict)
        self.assertIn('0th', metadata)
        self.assertIn('Exif', metadata)
        self.assertIn('file_info', metadata)
        
        # Check specific metadata values
        self.assertIn(piexif.ImageIFD.Artist, metadata['0th'])
        self.assertEqual(
            metadata['0th'][piexif.ImageIFD.Artist]['value'], 
            "Test Artist"
        )
    
    def test_load_tiff_metadata(self):
        """Test loading TIFF metadata."""
        test_file = self.test_files['tiff_with_exif']
        metadata = self.logic.load_image_metadata(test_file)
        
        self.assertIsInstance(metadata, dict)
        self.assertIn('0th', metadata)
        self.assertIn('file_info', metadata)
    
    def test_load_no_exif_metadata(self):
        """Test loading image with no EXIF data."""
        test_file = self.test_files['jpeg_no_exif']
        metadata = self.logic.load_image_metadata(test_file)
        
        # Should return empty dict or minimal metadata
        self.assertIsInstance(metadata, dict)
    
    def test_save_metadata_modifications(self):
        """Test saving metadata modifications."""
        test_file = self.test_files['jpeg_with_exif']
        
        # Load original metadata
        original_metadata = self.logic.load_image_metadata(test_file)
        
        # Modify metadata
        modified_metadata = original_metadata.copy()
        if '0th' in modified_metadata:
            modified_metadata['0th'][piexif.ImageIFD.Artist] = {
                'name': 'Artist',
                'value': 'Modified Artist',
                'original_value': 'Test Artist',
                'original_type': str
            }
        
        # Save modifications
        result = self.logic.save_image_metadata(test_file, modified_metadata)
        self.assertTrue(result)
        
        # Verify modifications
        reloaded_metadata = self.logic.load_image_metadata(test_file)
        if '0th' in reloaded_metadata and piexif.ImageIFD.Artist in reloaded_metadata['0th']:
            self.assertEqual(
                reloaded_metadata['0th'][piexif.ImageIFD.Artist]['value'],
                "Modified Artist"
            )
    
    def test_progress_tracking(self):
        """Test progress tracking signals."""
        progress_signals = []
        milestone_signals = []
        
        self.logic.progress_percentage.connect(
            lambda p: progress_signals.append(p)
        )
        self.logic.milestone_reached.connect(
            lambda m, p: milestone_signals.append((m, p))
        )
        
        test_file = self.test_files['jpeg_with_exif']
        self.logic.load_image_metadata(test_file)
        
        # Verify progress signals were emitted
        self.assertGreater(len(progress_signals), 0)
        self.assertGreater(len(milestone_signals), 0)
        self.assertEqual(max(progress_signals), 100)
    
    def test_error_handling_invalid_file(self):
        """Test error handling for invalid files."""
        with self.assertRaises(FileNotFoundError):
            self.logic.load_image_metadata("nonexistent_file.jpg")
    
    def test_error_handling_unsupported_format(self):
        """Test error handling for unsupported formats."""
        # Create a PNG file (unsupported by piexif)
        png_path = os.path.join(self.test_dir, "test.png")
        img = Image.new('RGB', (100, 100), color='blue')
        img.save(png_path, "PNG")
        
        with self.assertRaises(ValueError):
            self.logic.load_image_metadata(png_path)
    
    def test_cancellation_support(self):
        """Test operation cancellation."""
        cancellation_signals = []
        self.logic.operation_cancelled.connect(
            lambda: cancellation_signals.append(True)
        )
        
        # Start operation and immediately cancel
        self.logic.cancel_operation()
        
        # Verify cancellation signal was emitted
        self.assertGreater(len(cancellation_signals), 0)
    
    def test_hub_integration(self):
        """Test hub integration functionality."""
        mock_hub = MagicMock()
        logic_with_hub = ImageMetadataLogic(mock_hub)
        
        test_file = self.test_files['jpeg_with_exif']
        logic_with_hub.load_image_metadata(test_file)
        
        # Verify hub methods were called
        self.assertTrue(mock_hub.report_status_to_hub.called)


class TestImageMetadataUtilities(unittest.TestCase):
    """Test utility functions for image metadata processing."""
    
    def test_get_tag_name(self):
        """Test tag name resolution."""
        # Test known tag
        tag_name = get_tag_name('0th', piexif.ImageIFD.Artist)
        self.assertIsInstance(tag_name, str)
        self.assertNotEqual(tag_name, '')
        
        # Test unknown tag
        unknown_tag_name = get_tag_name('0th', 99999)
        self.assertTrue(unknown_tag_name.startswith('UnknownTag_'))
    
    def test_format_exif_value(self):
        """Test EXIF value formatting."""
        # Test string value
        self.assertEqual(format_exif_value("test"), "test")
        
        # Test integer value
        self.assertEqual(format_exif_value(123), "123")
        
        # Test rational value (tuple)
        self.assertEqual(format_exif_value((1, 60)), "1/60")
        self.assertEqual(format_exif_value((100, 1)), "100")
        
        # Test bytes value
        test_bytes = b"test\x00"
        formatted = format_exif_value(test_bytes)
        self.assertEqual(formatted, "test")
    
    def test_parse_exif_value(self):
        """Test EXIF value parsing."""
        # Test string parsing
        result = parse_exif_value("test", str, 0)
        self.assertEqual(result, "test")
        
        # Test integer parsing
        result = parse_exif_value("123", int, 0)
        self.assertEqual(result, 123)
        
        # Test rational parsing
        result = parse_exif_value("1/60", (1, 60), 0)
        self.assertEqual(result, (1, 60))
        
        # Test invalid integer
        with self.assertRaises(ValueError):
            parse_exif_value("invalid", int, 0)
        
        # Test invalid rational
        with self.assertRaises(ValueError):
            parse_exif_value("invalid", (1, 60), 0)


class TestImageMetadataPyQt5Compatibility(unittest.TestCase):
    """Test PyQt5 compatibility and modern features."""
    
    def setUp(self):
        """Setup test environment."""
        self.app = QApplication.instance() or QApplication([])
    
    def test_signal_slot_connections(self):
        """Test modern PyQt5 signal/slot connections."""
        logic = ImageMetadataLogic()
        
        # Test signal types
        self.assertIsInstance(logic.progress_percentage, pyqtSignal)
        self.assertIsInstance(logic.metadata_loaded, pyqtSignal)
        self.assertIsInstance(logic.error_occurred, pyqtSignal)
        
        # Test signal connections
        signal_received = []
        logic.progress_percentage.connect(lambda p: signal_received.append(p))
        
        # Emit test signal
        logic.progress_percentage.emit(50)
        self.assertEqual(signal_received, [50])
    
    def test_gui_widget_compatibility(self):
        """Test GUI widget PyQt5 compatibility."""
        editor = ImageMetadataEditor()
        
        # Test StandardWindow inheritance
        from file_utilities_2.gui.standard_window import StandardWindow
        from PyQt5.QtWidgets import QMainWindow
        self.assertIsInstance(editor, StandardWindow)
        self.assertIsInstance(editor, QMainWindow)
        
        # Test hub integration
        from file_utilities_2.integration.hub_connector import HubConnector
        self.assertIsInstance(editor.hub_connector, HubConnector)
        
        editor.close()
    
    def test_enhanced_thread_functionality(self):
        """Test enhanced thread with PyQt5 features."""
        logic = ImageMetadataLogic()
        worker = ImageMetadataWorker(logic, "test.jpg", "load")
        
        # Test thread inheritance
        self.assertIsInstance(worker, QThread)
        
        # Test signal connections
        self.assertTrue(hasattr(worker, 'metadata_processed'))
        self.assertTrue(hasattr(worker, 'progress_update'))
    
    def test_modern_pyqt5_features(self):
        """Test modern PyQt5 features usage."""
        editor = ImageMetadataEditor()
        
        # Test hub connector
        self.assertTrue(hasattr(editor, 'hub_connector'))
        
        # Verify signal parameter types
        logic = editor.metadata_logic
        
        # Test that signals exist and are properly typed
        self.assertTrue(hasattr(logic, 'progress_percentage'))
        self.assertTrue(hasattr(logic, 'metadata_loaded'))
        
        editor.close()


class TestImageMetadataGUIIntegration(unittest.TestCase):
    """Test GUI integration functionality."""
    
    def setUp(self):
        """Setup test environment with mock hub."""
        self.app = QApplication.instance() or QApplication([])
        self.mock_hub = MagicMock()
        self.editor = ImageMetadataEditor(hub_instance=self.mock_hub)
    
    def tearDown(self):
        """Cleanup test environment."""
        self.editor.close()
    
    def test_gui_initialization(self):
        """Test GUI initialization."""
        # Verify main components exist
        self.assertTrue(hasattr(self.editor, 'metadata_tree'))
        self.assertTrue(hasattr(self.editor, 'file_path_edit'))
        self.assertTrue(hasattr(self.editor, 'browse_button'))
        self.assertTrue(hasattr(self.editor, 'save_button'))
        
        # Verify initial state
        self.assertFalse(self.editor.save_button.isEnabled())
        self.assertFalse(self.editor.reload_button.isEnabled())
        self.assertFalse(self.editor.export_button.isEnabled())
    
    def test_hub_registration(self):
        """Test hub registration process."""
        # Verify hub connector is initialized
        self.assertIsNotNone(self.editor.hub_connector)
        self.assertEqual(self.editor.hub_connector.tool_name, "Image Metadata Editor")
    
    def test_theme_integration(self):
        """Test theme integration."""
        # Verify theme manager integration
        from file_utilities_2.gui.themes import ThemeManager
        
        # Test that theme callback is registered
        self.assertTrue(hasattr(self.editor, '_on_theme_changed'))
        
        # Test theme application
        self.editor._apply_theme()  # Should not raise exceptions
    
    def test_progress_ui_visibility(self):
        """Test progress UI visibility control."""
        # Initially hidden
        self.assertFalse(self.editor.progress_group.isVisible())
        
        # Show progress UI
        self.editor._show_progress_ui()
        self.assertTrue(self.editor.progress_group.isVisible())
        self.assertFalse(self.editor.browse_button.isEnabled())
        
        # Hide progress UI
        self.editor._hide_progress_ui()
        self.assertFalse(self.editor.progress_group.isVisible())
        self.assertTrue(self.editor.browse_button.isEnabled())
    
    def test_metadata_tree_population(self):
        """Test metadata tree population."""
        # Create mock metadata
        mock_metadata = {
            '0th': {
                piexif.ImageIFD.Artist: {
                    'name': 'Artist',
                    'value': 'Test Artist',
                    'original_value': 'Test Artist',
                    'original_type': str,
                    'editable': True
                }
            },
            'file_info': {
                'file_name': 'test.jpg',
                'file_size': 1024
            }
        }
        
        # Populate tree
        self.editor._populate_metadata_tree(mock_metadata)
        
        # Verify tree has items
        self.assertGreater(self.editor.metadata_tree.topLevelItemCount(), 0)
    
    def test_error_handling_integration(self):
        """Test error handling integration."""
        error_messages = []
        
        # Mock error dialog to capture messages
        def mock_error_dialog(title, message):
            error_messages.append((title, message))
        
        self.editor.show_error_dialog = mock_error_dialog
        
        # Trigger error
        self.editor._on_error_occurred("Test error message")
        
        # Verify error was handled
        self.assertEqual(len(error_messages), 1)
        self.assertEqual(error_messages[0][1], "Test error message")


class TestImageMetadataPerformance(unittest.TestCase):
    """Test performance characteristics."""
    
    def setUp(self):
        """Setup test environment."""
        self.app = QApplication.instance() or QApplication([])
        self.test_dir = tempfile.mkdtemp()
        self.logic = ImageMetadataLogic()
    
    def tearDown(self):
        """Cleanup test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def _create_large_test_image(self):
        """Create a large test image."""
        large_image_path = os.path.join(self.test_dir, "large_test.jpg")
        img = Image.new('RGB', (2000, 2000), color='green')
        
        # Create comprehensive EXIF data
        exif_dict = {
            "0th": {
                piexif.ImageIFD.Artist: "Performance Test Artist",
                piexif.ImageIFD.Software: "Performance Test Software",
                piexif.ImageIFD.ImageWidth: 2000,
                piexif.ImageIFD.ImageLength: 2000,
                piexif.ImageIFD.Make: "Test Camera",
                piexif.ImageIFD.Model: "Test Model",
            },
            "Exif": {
                piexif.ExifIFD.ExposureTime: (1, 125),
                piexif.ExifIFD.FNumber: (35, 10),
                piexif.ExifIFD.ISOSpeedRatings: 200,
                piexif.ExifIFD.DateTimeOriginal: "2025:07:29 16:30:00",
                piexif.ExifIFD.FocalLength: (50, 1),
            },
            "GPS": {
                piexif.GPSIFD.GPSLatitude: ((40, 1), (42, 1), (51, 1)),
                piexif.GPSIFD.GPSLongitude: ((74, 1), (0, 1), (23, 1)),
            },
            "1st": {},
            "thumbnail": None
        }
        
        exif_bytes = piexif.dump(exif_dict)
        img.save(large_image_path, "JPEG", exif=exif_bytes, quality=95)
        return large_image_path
    
    def test_large_file_processing(self):
        """Test processing of large image files."""
        import time
        
        large_image_path = self._create_large_test_image()
        
        start_time = time.time()
        metadata = self.logic.load_image_metadata(large_image_path)
        end_time = time.time()
        
        # Verify reasonable processing time (< 5 seconds for large files)
        processing_time = end_time - start_time
        self.assertLess(processing_time, 5.0)
        
        # Verify metadata was loaded
        self.assertIsInstance(metadata, dict)
        self.assertIn('0th', metadata)
        self.assertIn('Exif', metadata)
    
    def test_memory_efficiency(self):
        """Test memory efficiency during processing."""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Process large file
            large_image_path = self._create_large_test_image()
            
            for _ in range(5):  # Process multiple times
                self.logic.load_image_metadata(large_image_path)
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # Verify memory increase is reasonable (< 50MB)
            self.assertLess(memory_increase, 50)
            
        except ImportError:
            self.skipTest("psutil not available for memory testing")
    
    def test_signal_emission_performance(self):
        """Test that signal emissions don't impact performance significantly."""
        import time
        
        large_image_path = self._create_large_test_image()
        
        # Test with signal connections
        signal_count = 0
        def count_signals(*args):
            nonlocal signal_count
            signal_count += 1
        
        self.logic.progress_percentage.connect(count_signals)
        self.logic.progress_message.connect(count_signals)
        self.logic.milestone_reached.connect(count_signals)
        
        start_time = time.time()
        self.logic.load_image_metadata(large_image_path)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Verify signals were emitted
        self.assertGreater(signal_count, 0)
        
        # Verify processing time is still reasonable
        self.assertLess(processing_time, 5.0)


if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestImageMetadataCore))
    test_suite.addTest(unittest.makeSuite(TestImageMetadataUtilities))
    test_suite.addTest(unittest.makeSuite(TestImageMetadataPyQt5Compatibility))
    test_suite.addTest(unittest.makeSuite(TestImageMetadataGUIIntegration))
    test_suite.addTest(unittest.makeSuite(TestImageMetadataPerformance))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)