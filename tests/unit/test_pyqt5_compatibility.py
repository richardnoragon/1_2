"""
PyQt5 Compatibility and Performance Validation Tests

This module contains comprehensive tests to validate PyQt5 compatibility,
performance, and the enhanced progress tracking system.
"""

import sys
import os
import time
import tempfile
import unittest
from unittest.mock import Mock, patch
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, QTimer, pyqtSignal
from PyQt5.QtTest import QTest

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from file_utilities_2.core.check_sum import ChecksumLogic, VALID_ALGORITHMS
from file_utilities_2.gui.check_sum_standardized import ChecksumWindow, EnhancedChecksumThread


class PyQt5CompatibilityTest(unittest.TestCase):
    """Test PyQt5 compatibility and modern features."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test files
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, 'test_file.txt')
        with open(self.test_file, 'w') as f:
            f.write('Test content for PyQt5 compatibility testing\n' * 1000)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_pyqt5_signal_slot_connections(self):
        """Test modern PyQt5 signal/slot connections."""
        checksummer = ChecksumLogic(
            self.test_file,
            'sha256',
            mode='calculate_file'
        )
        
        # Test signal existence
        self.assertTrue(hasattr(checksummer, 'progress_percentage'))
        self.assertTrue(hasattr(checksummer, 'progress_message'))
        self.assertTrue(hasattr(checksummer, 'milestone_reached'))
        self.assertTrue(hasattr(checksummer, 'time_estimate'))
        
        # Test signal types
        self.assertIsInstance(checksummer.progress_percentage, pyqtSignal)
        self.assertIsInstance(checksummer.progress_message, pyqtSignal)
        self.assertIsInstance(checksummer.milestone_reached, pyqtSignal)
        self.assertIsInstance(checksummer.time_estimate, pyqtSignal)
    
    def test_enhanced_thread_functionality(self):
        """Test enhanced thread with PyQt5 features."""
        thread = EnhancedChecksumThread(self.test_file, 'sha256')
        
        # Test thread signals
        self.assertTrue(hasattr(thread, 'progress_percentage'))
        self.assertTrue(hasattr(thread, 'progress_message'))
        self.assertTrue(hasattr(thread, 'milestone_reached'))
        self.assertTrue(hasattr(thread, 'time_estimate'))
        
        # Test cancellation support
        self.assertTrue(hasattr(thread, 'cancel'))
        self.assertFalse(thread._cancelled)
        
        thread.cancel()
        self.assertTrue(thread._cancelled)
    
    def test_gui_widget_compatibility(self):
        """Test GUI widget PyQt5 compatibility."""
        window = ChecksumWindow()
        
        # Test widget creation
        self.assertIsNotNone(window.progress_bar)
        self.assertIsNotNone(window.progress_message)
        self.assertIsNotNone(window.time_estimate_label)
        self.assertIsNotNone(window.cancel_button)
        
        # Test widget properties
        self.assertFalse(window.progress_bar.isVisible())
        self.assertFalse(window.progress_message.isVisible())
        self.assertFalse(window.time_estimate_label.isVisible())
        self.assertFalse(window.cancel_button.isVisible())
        
        window.close()
    
    def test_modern_pyqt5_features(self):
        """Test modern PyQt5 features usage."""
        window = ChecksumWindow()
        
        # Test QTimer usage
        self.assertIsInstance(window.progress_timer, QTimer)
        
        # Test signal connections
        window._show_progress_ui()
        self.assertTrue(window.progress_group.isVisible())
        self.assertTrue(window.progress_bar.isVisible())
        
        window._hide_progress_ui()
        self.assertFalse(window.progress_group.isVisible())
        
        window.close()


class ProgressTrackingPerformanceTest(unittest.TestCase):
    """Test progress tracking performance and efficiency."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        # Create a larger test file for performance testing
        self.large_test_file = os.path.join(self.test_dir, 'large_test.txt')
        with open(self.large_test_file, 'w') as f:
            # Write ~1MB of data
            for i in range(10000):
                f.write(f'Line {i}: This is test data for performance testing\n')
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_progress_update_frequency(self):
        """Test that progress updates don't overwhelm the system."""
        class ProgressCounter:
            def __init__(self):
                self.count = 0
                self.start_time = None
                self.end_time = None
            
            def count_update(self, percentage):
                if self.start_time is None:
                    self.start_time = time.time()
                self.count += 1
                self.end_time = time.time()
        
        counter = ProgressCounter()
        
        checksummer = ChecksumLogic(
            self.large_test_file,
            'sha256',
            mode='calculate_file'
        )
        
        checksummer.progress_percentage.connect(counter.count_update)
        
        start_time = time.time()
        checksummer.run()
        end_time = time.time()
        
        # Verify reasonable update frequency
        total_time = end_time - start_time
        if counter.count > 0 and total_time > 0:
            updates_per_second = counter.count / total_time
            # Should not exceed 100 updates per second (reasonable throttling)
            self.assertLess(updates_per_second, 100)
    
    def test_memory_efficiency(self):
        """Test memory efficiency during large file processing."""
        import psutil
        import gc
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        checksummer = ChecksumLogic(
            self.large_test_file,
            'sha256',
            mode='calculate_file'
        )
        
        checksummer.run()
        
        # Force garbage collection
        gc.collect()
        
        # Get final memory usage
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB for this test)
        self.assertLess(memory_increase, 50 * 1024 * 1024)
    
    def test_cancellation_responsiveness(self):
        """Test that cancellation is responsive."""
        checksummer = ChecksumLogic(
            self.large_test_file,
            'sha256',
            mode='calculate_file'
        )
        
        start_time = time.time()
        
        # Start operation in thread
        thread = QThread()
        checksummer.moveToThread(thread)
        
        # Cancel after short delay
        QTimer.singleShot(100, checksummer.stop)  # Cancel after 100ms
        
        thread.started.connect(checksummer.run)
        thread.start()
        
        # Wait for thread to finish
        thread.wait(5000)  # 5 second timeout
        
        end_time = time.time()
        operation_time = end_time - start_time
        
        # Operation should complete quickly due to cancellation
        self.assertLess(operation_time, 2.0)  # Should finish within 2 seconds
    
    def test_signal_emission_performance(self):
        """Test that signal emissions don't impact performance significantly."""
        class SignalReceiver:
            def __init__(self):
                self.signal_count = 0
            
            def receive_signal(self, *args):
                self.signal_count += 1
        
        receiver = SignalReceiver()
        
        checksummer = ChecksumLogic(
            self.large_test_file,
            'sha256',
            mode='calculate_file'
        )
        
        # Connect all signals
        checksummer.progress_percentage.connect(receiver.receive_signal)
        checksummer.progress_message.connect(receiver.receive_signal)
        checksummer.milestone_reached.connect(receiver.receive_signal)
        checksummer.time_estimate.connect(receiver.receive_signal)
        
        # Time operation with signals
        start_time = time.time()
        checksummer.run()
        end_time = time.time()
        
        signal_time = end_time - start_time
        
        # Compare with operation without signals
        checksummer_no_signals = ChecksumLogic(
            self.large_test_file,
            'sha256',
            mode='calculate_file'
        )
        
        start_time = time.time()
        checksummer_no_signals.run()
        end_time = time.time()
        
        no_signal_time = end_time - start_time
        
        # Signal overhead should be minimal (less than 50% increase)
        if no_signal_time > 0:
            overhead_ratio = signal_time / no_signal_time
            self.assertLess(overhead_ratio, 1.5)


class IntegrationTest(unittest.TestCase):
    """Integration tests for complete PyQt5 system."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, 'integration_test.txt')
        with open(self.test_file, 'w') as f:
            f.write('Integration test content\n' * 500)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_complete_workflow(self):
        """Test complete workflow from GUI to core logic."""
        window = ChecksumWindow()
        
        # Set up file path
        window.file_path_input.setText(self.test_file)
        window.algorithm_combo.setCurrentText('sha256')
        
        # Track progress updates
        progress_updates = []
        message_updates = []
        
        def track_progress(percentage):
            progress_updates.append(percentage)
        
        def track_message(message):
            message_updates.append(message)
        
        # Start calculation
        window.calculate_checksum()
        
        # Verify thread was created
        self.assertIsNotNone(window.checksum_thread)
        self.assertIsInstance(window.checksum_thread, EnhancedChecksumThread)
        
        # Wait for completion
        if window.checksum_thread.isRunning():
            window.checksum_thread.wait(5000)
        
        window.close()
    
    def test_error_handling_integration(self):
        """Test error handling throughout the system."""
        window = ChecksumWindow()
        
        # Set invalid file path
        window.file_path_input.setText('/nonexistent/file.txt')
        
        # Attempt calculation
        window.calculate_checksum()
        
        # Should show error message
        self.assertEqual(window.status_bar.currentMessage(), 
                        "Please select a valid file")
        
        window.close()
    
    def test_cancellation_integration(self):
        """Test cancellation integration between GUI and core."""
        window = ChecksumWindow()
        
        # Set up file path
        window.file_path_input.setText(self.test_file)
        
        # Start calculation
        window.calculate_checksum()
        
        # Immediately cancel
        if window.checksum_thread:
            window.cancel_operation()
            
            # Wait briefly for cancellation
            QTest.qWait(100)
            
            # Verify cancellation
            self.assertTrue(window.checksum_thread._cancelled)
        
        window.close()


def run_compatibility_tests():
    """Run all PyQt5 compatibility tests."""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(PyQt5CompatibilityTest))
    suite.addTest(unittest.makeSuite(ProgressTrackingPerformanceTest))
    suite.addTest(unittest.makeSuite(IntegrationTest))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_compatibility_tests()
    sys.exit(0 if success else 1)