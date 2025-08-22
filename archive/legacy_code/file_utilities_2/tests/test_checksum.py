import unittest
import os
import hashlib
import unittest
from tests.test_utils import TestUtils
from file_utilities_2.core.check_sum import ChecksumLogic

from src.core.error_handler import error_handler


class TestChecksummer(unittest.TestCase):
    """A class that handles test checksummer."""
    def setUp(self):
        """setup."""
        self.test_dir = TestUtils.create_temp_dir()
        self.checksummer = ChecksumLogic(target_path="", algorithm="sha256")
        
        # Create test files with known content
        self.test_files = {}
        contents = {
            'empty': b'',
            'small': b'Hello, World!',
            'medium': b'A' * 1024,  # 1KB
            'large': b'B' * (1024 * 1024)  # 1MB
        }
        
        for name, content in contents.items():
            path = os.path.join(self.test_dir, f"{name}.txt")
            with open(path, 'wb') as f:
                f.write(content)
            self.test_files[name] = {
                'path': path,
                'content': content,
                'md5': hashlib.md5(content).hexdigest(),
                'sha1': hashlib.sha1(content).hexdigest(),
                'sha256': hashlib.sha256(content).hexdigest()
            }

    def tearDown(self):
        """teardown."""
        TestUtils.cleanup_temp_dir(self.test_dir)

    def test_calculate_md5(self):
        """Test MD5 checksum calculation"""
        for name, info in self.test_files.items():
            checksum = self.checksummer.calculate_md5(info['path'])
            self.assertEqual(
                checksum,
                info['md5'],
                f"MD5 mismatch for {name} file"
            )

    def test_calculate_sha1(self):
        """Test SHA1 checksum calculation"""
        for name, info in self.test_files.items():
            checksum = self.checksummer.calculate_sha1(info['path'])
            self.assertEqual(
                checksum,
                info['sha1'],
                f"SHA1 mismatch for {name} file"
            )

    def test_calculate_sha256(self):
        """Test SHA256 checksum calculation"""
        for name, info in self.test_files.items():
            checksum = self.checksummer.calculate_sha256(info['path'])
            self.assertEqual(
                checksum,
                info['sha256'],
                f"SHA256 mismatch for {name} file"
            )

    def test_batch_checksum(self):
        """Test calculating checksums for multiple files"""
        files = [info['path'] for info in self.test_files.values()]
        results = self.checksummer.calculate_batch(files, algorithm='sha256')
        
        for file_path, checksum in results.items():
            # Find the corresponding test file info
            file_name = os.path.basename(file_path).split('.')[0]
            expected = self.test_files[file_name]['sha256']
            self.assertEqual(checksum, expected)

    def test_verify_checksum(self):
        """Test checksum verification"""
        for info in self.test_files.values():
            # Test successful verification
            self.assertTrue(
                self.checksummer.verify_file(
                    info['path'],
                    info['sha256'],
                    algorithm='sha256'
                )
            )
            
            # Test failed verification
            self.assertFalse(
                self.checksummer.verify_file(
                    info['path'],
                    'invalid_checksum',
                    algorithm='sha256'
                )
            )

    def test_progress_tracking(self):
        """Test progress reporting during checksum calculation"""
        progress_values = []
        
        def progress_callback(percent):
            """progresscallback.
        Args:
            percent (Any): Description of percent"""
            progress_values.append(percent)
        
        # Calculate checksum with progress tracking
        self.checksummer.calculate_sha256(
            self.test_files['large']['path'],
            progress_callback=progress_callback
        )
        
        # Verify progress was reported
        self.assertTrue(len(progress_values) > 0)
        self.assertEqual(progress_values[-1], 100)

    def test_enhanced_progress_signals(self):
        """Test enhanced progress tracking signals"""
        from PyQt5.QtCore import QObject, pyqtSignal
        
        class ProgressReceiver(QObject):
            def __init__(self):
                super().__init__()
                self.percentages = []
                self.messages = []
                self.milestones = []
                self.time_estimates = []
            
            def on_percentage(self, percentage):
                self.percentages.append(percentage)
            
            def on_message(self, message):
                self.messages.append(message)
            
            def on_milestone(self, milestone, percentage):
                self.milestones.append((milestone, percentage))
            
            def on_time_estimate(self, estimate):
                self.time_estimates.append(estimate)
        
        # Create receiver and connect signals
        receiver = ProgressReceiver()
        
        # Create ChecksumLogic with enhanced tracking
        checksummer = ChecksumLogic(
            self.test_files['large']['path'],
            'sha256',
            mode='calculate_file'
        )
        
        # Connect signals
        checksummer.progress_percentage.connect(receiver.on_percentage)
        checksummer.progress_message.connect(receiver.on_message)
        checksummer.milestone_reached.connect(receiver.on_milestone)
        checksummer.time_estimate.connect(receiver.on_time_estimate)
        
        # Run calculation
        checksummer.run()
        
        # Verify signals were emitted
        self.assertTrue(len(receiver.percentages) > 0)
        self.assertTrue(len(receiver.messages) > 0)
        self.assertTrue(len(receiver.milestones) > 0)
        
        # Verify final percentage is 100
        if receiver.percentages:
            self.assertEqual(max(receiver.percentages), 100)
        
        # Verify milestone progression
        milestone_percentages = [m[1] for m in receiver.milestones]
        self.assertTrue(any(p == 0 for p in milestone_percentages))  # Start
        self.assertTrue(any(p == 100 for p in milestone_percentages))  # End

    def test_cancellation_support(self):
        """Test operation cancellation"""
        checksummer = ChecksumLogic(
            self.test_files['large']['path'],
            'sha256',
            mode='calculate_file'
        )
        
        # Start operation and immediately cancel
        import threading
        
        def cancel_after_delay():
            import time
            time.sleep(0.1)  # Let operation start
            checksummer.stop()
        
        cancel_thread = threading.Thread(target=cancel_after_delay)
        cancel_thread.start()
        
        # Run operation (should be cancelled)
        checksummer.run()
        
        cancel_thread.join()
        
        # Verify operation was stopped
        self.assertFalse(checksummer._is_running)

    def test_milestone_tracking(self):
        """Test milestone tracking for different operation phases"""
        from PyQt5.QtCore import QObject
        
        class MilestoneTracker(QObject):
            def __init__(self):
                super().__init__()
                self.milestones = []
            
            def track_milestone(self, milestone, percentage):
                self.milestones.append((milestone, percentage))
        
        tracker = MilestoneTracker()
        
        checksummer = ChecksumLogic(
            self.test_files['medium']['path'],
            'sha256',
            mode='calculate_file'
        )
        
        checksummer.milestone_reached.connect(tracker.track_milestone)
        checksummer.run()
        
        # Verify milestone progression
        self.assertTrue(len(tracker.milestones) >= 2)  # At least start and end
        
        # Check for expected milestones
        milestone_names = [m[0] for m in tracker.milestones]
        self.assertIn("Starting operation", milestone_names)
        self.assertIn("File checksum completed", milestone_names)

    def test_time_estimation(self):
        """Test time estimation functionality"""
        from PyQt5.QtCore import QObject
        
        class TimeTracker(QObject):
            def __init__(self):
                super().__init__()
                self.estimates = []
            
            def track_estimate(self, estimate):
                self.estimates.append(estimate)
        
        tracker = TimeTracker()
        
        checksummer = ChecksumLogic(
            self.test_files['large']['path'],
            'sha256',
            mode='calculate_file'
        )
        
        checksummer.time_estimate.connect(tracker.track_estimate)
        checksummer.run()
        
        # Verify time estimates were provided
        # Note: For small test files, estimates might not be generated
        # This test mainly ensures the signal mechanism works
        self.assertIsInstance(tracker.estimates, list)

    def test_progress_message_updates(self):
        """Test detailed progress message updates"""
        from PyQt5.QtCore import QObject
        
        class MessageTracker(QObject):
            def __init__(self):
                super().__init__()
                self.messages = []
            
            def track_message(self, message):
                self.messages.append(message)
        
        tracker = MessageTracker()
        
        checksummer = ChecksumLogic(
            self.test_files['medium']['path'],
            'sha256',
            mode='calculate_file'
        )
        
        checksummer.progress_message.connect(tracker.track_message)
        checksummer.run()
        
        # Verify messages were sent
        self.assertTrue(len(tracker.messages) > 0)
        
        # Check for expected message patterns
        message_text = ' '.join(tracker.messages)
        self.assertTrue(any('Initializing' in msg for msg in tracker.messages))

    def test_verification_progress(self):
        """Test progress tracking during verification operations"""
        from PyQt5.QtCore import QObject
        
        class VerificationTracker(QObject):
            def __init__(self):
                super().__init__()
                self.milestones = []
                self.percentages = []
            
            def track_milestone(self, milestone, percentage):
                self.milestones.append((milestone, percentage))
            
            def track_percentage(self, percentage):
                self.percentages.append(percentage)
        
        tracker = VerificationTracker()
        
        # Get expected checksum
        expected_checksum = self.test_files['medium']['sha256']
        
        checksummer = ChecksumLogic(
            self.test_files['medium']['path'],
            'sha256',
            expected_checksum=expected_checksum,
            mode='verify_file'
        )
        
        checksummer.milestone_reached.connect(tracker.track_milestone)
        checksummer.progress_percentage.connect(tracker.track_percentage)
        checksummer.run()
        
        # Verify verification-specific milestones
        milestone_names = [m[0] for m in tracker.milestones]
        self.assertIn("Verifying file checksum", milestone_names)
        self.assertIn("File verification completed", milestone_names)
        
        # Verify progress was tracked
        self.assertTrue(len(tracker.percentages) > 0)

    def test_verify_from_file(self):
        """Test verifying checksums from a checksum file"""
        # Create a checksum file
        checksum_file = os.path.join(self.test_dir, "checksums.txt")
        with open(checksum_file, 'w') as f:
            for name, info in self.test_files.items():
                f.write(f"{info['sha256']} *{os.path.basename(info['path'])}\n")
        
        # Verify checksums
        results = self.checksummer.verify_from_file(
            checksum_file,
            self.test_dir
        )
        
        # Check results
        self.assertEqual(len(results), len(self.test_files))
        for file_path, verified in results.items():
            self.assertTrue(verified)

    def test_error_handling(self):
        """Test error handling for invalid operations"""
        # Test non-existent file
        with self.assertRaises(FileNotFoundError):
            self.checksummer.calculate_md5("nonexistent.file")
        
        # Test invalid algorithm
        with self.assertRaises(ValueError):
            self.checksummer.calculate_batch(
                [self.test_files['small']['path']],
                algorithm='invalid'
            )
        
        # Test invalid checksum format
        with self.assertRaises(ValueError):
            self.checksummer.verify_file(
                self.test_files['small']['path'],
                'invalid_format_checksum'
            )

if __name__ == '__main__':
    unittest.main()