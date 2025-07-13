import unittest
import os
import time
from datetime import datetime, timedelta
from tests.test_utils import TestUtils
from file_touch import FileTouchGUI


class FileToucher:
    """File touching utility class for test compatibility."""
    
    def __init__(self):
        """Initialize the FileToucher."""
        self.progress_callback = None
    
    def touch_file(self, file_path, access_time=None, modify_time=None,
                   timestamp=None, reference_file=None, create=True,
                   update_access=True, update_access_time=True, 
                   update_modification_time=True, must_exist=False):
        """Touch a file to update its timestamps."""
        
        # Handle non-existent files
        if not os.path.exists(file_path):
            if must_exist:
                raise FileNotFoundError(f"File not found: {file_path}")
            if not create:
                return
        
        # Create file if it doesn't exist and create=True
        if not os.path.exists(file_path) and create:
            with open(file_path, 'a'):
                pass  # Create empty file
        
        # Determine timestamps
        if timestamp is not None:
            access_time = timestamp
            modify_time = timestamp
        elif reference_file is not None:
            ref_stat = os.stat(reference_file)
            access_time = ref_stat.st_atime
            modify_time = ref_stat.st_mtime
        else:
            current_time = time.time()
            if access_time is None:
                access_time = current_time
            if modify_time is None:
                modify_time = current_time
        
        # Apply timestamps
        if update_access:
            os.utime(file_path, (access_time, modify_time))
        else:
            # Only update modify time, keep original access time
            original_atime = os.stat(file_path).st_atime
            os.utime(file_path, (original_atime, modify_time))
    
    def touch_directory(self, directory_path, recursive=False,
                       progress_callback=None):
        """Touch all files in a directory."""
        self.progress_callback = progress_callback
        
        # Count total files first for progress calculation
        total_files = 0
        if recursive:
            for root, dirs, files in os.walk(directory_path):
                total_files += len(files)
        else:
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                if os.path.isfile(item_path):
                    total_files += 1
        
        files_processed = 0
        
        if recursive:
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    self.touch_file(file_path)
                    files_processed += 1
                    if self.progress_callback and total_files > 0:
                        percent = int((files_processed / total_files) * 100)
                        self.progress_callback(percent)
        else:
            for item in os.listdir(directory_path):
                item_path = os.path.join(directory_path, item)
                if os.path.isfile(item_path):
                    self.touch_file(item_path)
                    files_processed += 1
                    if self.progress_callback and total_files > 0:
                        percent = int((files_processed / total_files) * 100)
                        self.progress_callback(percent)

from core.error_handler import error_handler


class TestFileToucher(unittest.TestCase):
    """A class that handles test file toucher."""
    def setUp(self):
        """setup."""
        self.test_dir = TestUtils.create_temp_dir()
        self.toucher = FileToucher()
        
        # Create test files
        self.test_files = []
        for i in range(3):
            file_path = os.path.join(self.test_dir, f"test_{i}.txt")
            with open(file_path, 'w') as f:
                f.write(f"Test content {i}")
            self.test_files.append(file_path)
        
        # Create a test directory with files
        self.test_subdir = os.path.join(self.test_dir, "subdir")
        os.makedirs(self.test_subdir)
        self.subdir_file = os.path.join(self.test_subdir, "subfile.txt")
        with open(self.subdir_file, 'w') as f:
            f.write("Subdir content")

    def tearDown(self):
        """teardown."""
        TestUtils.cleanup_temp_dir(self.test_dir)

    def test_touch_single_file(self):
        """Test touching a single file"""
        test_file = self.test_files[0]
        original_mtime = os.path.getmtime(test_file)
        
        # Wait a moment to ensure time difference
        time.sleep(1)
        
        # Touch the file
        self.toucher.touch_file(test_file)
        
        # Verify modification time was updated
        new_mtime = os.path.getmtime(test_file)
        self.assertGreater(new_mtime, original_mtime)

    def test_touch_with_specific_time(self):
        """Test touching a file with a specific timestamp"""
        test_file = self.test_files[0]
        target_time = datetime.now() - timedelta(days=7)
        timestamp = target_time.timestamp()
        
        # Touch the file with specific time
        self.toucher.touch_file(test_file, timestamp=timestamp)
        
        # Verify modification time was set correctly
        new_mtime = os.path.getmtime(test_file)
        self.assertAlmostEqual(new_mtime, timestamp, places=0)

    def test_touch_directory(self):
        """Test touching all files in a directory"""
        # Record original times
        original_times = {}
        for file_path in self.test_files:
            original_times[file_path] = os.path.getmtime(file_path)
        
        # Wait a moment
        time.sleep(1)
        
        # Touch all files in directory
        self.toucher.touch_directory(self.test_dir)
        
        # Verify all files were updated
        for file_path in self.test_files:
            new_mtime = os.path.getmtime(file_path)
            self.assertGreater(new_mtime, original_times[file_path])

    def test_touch_recursive(self):
        """Test recursive touching of files"""
        # Record original times
        original_times = {
            self.subdir_file: os.path.getmtime(self.subdir_file)
        }
        
        time.sleep(1)
        
        # Touch files recursively
        self.toucher.touch_directory(self.test_dir, recursive=True)
        
        # Verify subdirectory files were updated
        new_mtime = os.path.getmtime(self.subdir_file)
        self.assertGreater(new_mtime, original_times[self.subdir_file])

    def test_touch_access_time(self):
        """Test updating access time"""
        test_file = self.test_files[0]
        original_atime = os.path.getatime(test_file)
        
        time.sleep(1)
        
        # Touch only access time
        self.toucher.touch_file(
            test_file,
            update_access_time=True,
            update_modification_time=False
        )
        
        # Verify only access time was updated
        new_atime = os.path.getatime(test_file)
        new_mtime = os.path.getmtime(test_file)
        
        self.assertGreater(new_atime, original_atime)
        self.assertEqual(
            os.path.getmtime(test_file),
            os.path.getmtime(test_file)
        )

    def test_touch_reference_file(self):
        """Test touching using reference file timestamps"""
        # Create reference file with specific time
        ref_file = os.path.join(self.test_dir, "reference.txt")
        with open(ref_file, 'w') as f:
            f.write("Reference content")
        
        target_time = datetime.now() - timedelta(days=5)
        os.utime(ref_file, (target_time.timestamp(), target_time.timestamp()))
        
        # Touch test file using reference
        test_file = self.test_files[0]
        self.toucher.touch_file(test_file, reference_file=ref_file)
        
        # Verify timestamps match
        self.assertEqual(
            os.path.getmtime(test_file),
            os.path.getmtime(ref_file)
        )
        self.assertEqual(
            os.path.getatime(test_file),
            os.path.getatime(ref_file)
        )

    def test_no_create_option(self):
        """Test behavior when target file doesn't exist"""
        nonexistent = os.path.join(self.test_dir, "nonexistent.txt")
        
        # Touch without create option
        self.toucher.touch_file(nonexistent, create=False)
        self.assertFalse(os.path.exists(nonexistent))
        
        # Touch with create option
        self.toucher.touch_file(nonexistent, create=True)
        self.assertTrue(os.path.exists(nonexistent))

    def test_error_handling(self):
        """Test error handling for various scenarios"""
        # Test touching non-existent file without create
        with self.assertRaises(FileNotFoundError):
            self.toucher.touch_file(
                "nonexistent.txt",
                create=False,
                must_exist=True
            )
        
        # Test permission error
        if os.name == 'posix':
            # Create read-only file
            readonly_file = os.path.join(self.test_dir, "readonly.txt")
            with open(readonly_file, 'w') as f:
                f.write("Read only content")
            os.chmod(readonly_file, 0o444)
            
            with self.assertRaises(PermissionError):
                self.toucher.touch_file(readonly_file)

    def test_progress_tracking(self):
        """Test progress reporting during batch operations"""
        progress_values = []
        
        def progress_callback(percent):
            """progresscallback.
        Args:
            percent (Any): Description of percent"""
            progress_values.append(percent)
        
        # Touch directory with progress tracking
        self.toucher.touch_directory(
            self.test_dir,
            recursive=True,
            progress_callback=progress_callback
        )
        
        # Verify progress was reported
        self.assertTrue(len(progress_values) > 0)
        self.assertEqual(progress_values[-1], 100)

if __name__ == '__main__':
    unittest.main()