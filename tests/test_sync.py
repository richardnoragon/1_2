import unittest
import os
import time
from tests.test_utils import TestUtils
from sync import FileSynchronizer  # Update based on actual class name

from core.error_handler import error_handler


class TestFileSynchronization(unittest.TestCase):
    def setUp(self):
        self.test_dir = TestUtils.create_temp_dir()
        self.synchronizer = FileSynchronizer()
        
        # Create source and destination directories
        self.source_dir = os.path.join(self.test_dir, "source")
        self.dest_dir = os.path.join(self.test_dir, "destination")
        os.makedirs(self.source_dir)
        os.makedirs(self.dest_dir)
        
        # Create some test files in source
        self.test_files = {}
        for i in range(3):
            name = f"file_{i}.txt"
            path = os.path.join(self.source_dir, name)
            with open(path, 'w') as f:
                f.write(f"Content {i}")
            self.test_files[name] = path
        
        # Create a subdirectory with files
        self.source_subdir = os.path.join(self.source_dir, "subdir")
        os.makedirs(self.source_subdir)
        self.subdir_file = os.path.join(self.source_subdir, "subfile.txt")
        with open(self.subdir_file, 'w') as f:
            f.write("Subdir content")

    def tearDown(self):
        TestUtils.cleanup_temp_dir(self.test_dir)

    def test_basic_sync(self):
        """Test basic directory synchronization"""
        # Perform sync
        self.synchronizer.sync_directories(self.source_dir, self.dest_dir)
        
        # Verify all files were copied
        for name, source_path in self.test_files.items():
            dest_path = os.path.join(self.dest_dir, name)
            self.assertTrue(os.path.exists(dest_path))
            with open(source_path, 'r') as f1, open(dest_path, 'r') as f2:
                self.assertEqual(f1.read(), f2.read())
        
        # Verify subdirectory was copied
        dest_subdir = os.path.join(self.dest_dir, "subdir")
        dest_subfile = os.path.join(dest_subdir, "subfile.txt")
        self.assertTrue(os.path.exists(dest_subfile))

    def test_incremental_sync(self):
        """Test incremental synchronization"""
        # Perform initial sync
        self.synchronizer.sync_directories(self.source_dir, self.dest_dir)
        
        # Modify a file in source
        modified_file = self.test_files['file_0.txt']
        time.sleep(1)  # Ensure modification time is different
        with open(modified_file, 'w') as f:
            f.write("Modified content")
        
        # Create a new file
        new_file = os.path.join(self.source_dir, "new_file.txt")
        with open(new_file, 'w') as f:
            f.write("New content")
        
        # Perform incremental sync
        self.synchronizer.sync_directories(self.source_dir, self.dest_dir)
        
        # Verify changes were synced
        dest_modified = os.path.join(self.dest_dir, "file_0.txt")
        with open(dest_modified, 'r') as f:
            self.assertEqual(f.read(), "Modified content")
        
        dest_new = os.path.join(self.dest_dir, "new_file.txt")
        self.assertTrue(os.path.exists(dest_new))

    def test_conflict_resolution(self):
        """Test handling of file conflicts"""
        # Perform initial sync
        self.synchronizer.sync_directories(self.source_dir, self.dest_dir)
        
        # Modify same file in both directories
        test_file = 'file_0.txt'
        source_path = os.path.join(self.source_dir, test_file)
        dest_path = os.path.join(self.dest_dir, test_file)
        
        time.sleep(1)  # Ensure different modification times
        with open(source_path, 'w') as f:
            f.write("Source modified")
        with open(dest_path, 'w') as f:
            f.write("Destination modified")
        
        # Sync with conflict resolution
        conflicts = self.synchronizer.sync_directories(
            self.source_dir,
            self.dest_dir,
            conflict_resolution='keep_newest'
        )
        
        # Verify conflict was detected and resolved
        self.assertEqual(len(conflicts), 1)
        self.assertIn(test_file, conflicts)

    def test_deletion_sync(self):
        """Test synchronization of deletions"""
        # Perform initial sync
        self.synchronizer.sync_directories(self.source_dir, self.dest_dir)
        
        # Delete a file from source
        os.remove(self.test_files['file_1.txt'])
        
        # Sync with deletion
        self.synchronizer.sync_directories(
            self.source_dir,
            self.dest_dir,
            delete=True
        )
        
        # Verify file was deleted from destination
        dest_path = os.path.join(self.dest_dir, "file_1.txt")
        self.assertFalse(os.path.exists(dest_path))

    def test_filters(self):
        """Test file filtering during sync"""
        # Create some files that should be excluded
        excluded_file = os.path.join(self.source_dir, "temp.tmp")
        with open(excluded_file, 'w') as f:
            f.write("Temporary content")
        
        # Sync with filters
        self.synchronizer.sync_directories(
            self.source_dir,
            self.dest_dir,
            exclude_patterns=['*.tmp', '*.temp']
        )
        
        # Verify excluded file wasn't copied
        dest_excluded = os.path.join(self.dest_dir, "temp.tmp")
        self.assertFalse(os.path.exists(dest_excluded))

    def test_progress_tracking(self):
        """Test progress reporting during sync"""
        progress_values = []
        
        def progress_callback(percent):
            progress_values.append(percent)
        
        # Perform sync with progress tracking
        self.synchronizer.sync_directories(
            self.source_dir,
            self.dest_dir,
            progress_callback=progress_callback
        )
        
        # Verify progress was reported
        self.assertTrue(len(progress_values) > 0)
        self.assertEqual(progress_values[-1], 100)

    def test_error_handling(self):
        """Test error handling during sync"""
        # Test non-existent source directory
        with self.assertRaises(FileNotFoundError):
            self.synchronizer.sync_directories(
                "nonexistent",
                self.dest_dir
            )
        
        # Test permission error
        if os.name == 'posix':
            # Make destination read-only
            os.chmod(self.dest_dir, 0o444)
            with self.assertRaises(PermissionError):
                self.synchronizer.sync_directories(
                    self.source_dir,
                    self.dest_dir
                )

    def test_dry_run(self):
        """Test dry run functionality"""
        # Perform dry run
        changes = self.synchronizer.sync_directories(
            self.source_dir,
            self.dest_dir,
            dry_run=True
        )
        
        # Verify changes were detected but not applied
        self.assertTrue(len(changes) > 0)
        self.assertFalse(os.path.exists(os.path.join(self.dest_dir, "file_0.txt")))

if __name__ == '__main__':
    unittest.main()