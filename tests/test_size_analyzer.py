import unittest
import os
import json
from tests.test_utils import TestUtils
from size_analyzer import SizeAnalyzer  # Update based on actual class name

from core.error_handler import error_handler


class TestSizeAnalyzer(unittest.TestCase):
    def setUp(self):
        self.test_dir = TestUtils.create_temp_dir()
        self.analyzer = SizeAnalyzer()
        
        # Create test directory structure with known sizes
        self.create_test_structure()

    def tearDown(self):
        TestUtils.cleanup_temp_dir(self.test_dir)

    def create_test_structure(self):
        """Create a test directory structure with various file sizes"""
        # Create main subdirectories
        self.dirs = {
            'docs': os.path.join(self.test_dir, "documents"),
            'media': os.path.join(self.test_dir, "media"),
            'code': os.path.join(self.test_dir, "code")
        }
        for dir_path in self.dirs.values():
            os.makedirs(dir_path)
        
        # Create files with known sizes
        self.files = {}
        
        # Documents (text files)
        for i in range(3):
            path = os.path.join(self.dirs['docs'], f"doc_{i}.txt")
            content = "Document content\n" * 1000  # ~15KB
            with open(path, 'w') as f:
                f.write(content)
            self.files[path] = len(content)
        
        # Media files (simulated)
        media_sizes = {
            'video.mp4': 1024 * 1024 * 10,  # 10MB
            'audio.mp3': 1024 * 1024 * 2,   # 2MB
            'image.jpg': 1024 * 100         # 100KB
        }
        for name, size in media_sizes.items():
            path = os.path.join(self.dirs['media'], name)
            with open(path, 'wb') as f:
                f.write(os.urandom(size))
            self.files[path] = size
        
        # Code files
        code_content = "def test_function():\n    pass\n" * 100
        for i in range(5):
            path = os.path.join(self.dirs['code'], f"module_{i}.py")
            with open(path, 'w') as f:
                f.write(code_content)
            self.files[path] = len(code_content)

    def test_analyze_directory(self):
        """Test basic directory size analysis"""
        analysis = self.analyzer.analyze_directory(self.test_dir)
        
        # Verify total size
        expected_total = sum(self.files.values())
        self.assertEqual(analysis['total_size'], expected_total)
        
        # Verify file count
        self.assertEqual(analysis['file_count'], len(self.files))
        
        # Verify directory count
        self.assertEqual(
            analysis['directory_count'],
            len(self.dirs)  # Main directories
        )

    def test_file_type_summary(self):
        """Test file type statistics"""
        analysis = self.analyzer.analyze_directory(self.test_dir)
        type_stats = analysis['file_types']
        
        # Verify all file types are present
        self.assertIn('.txt', type_stats)
        self.assertIn('.mp4', type_stats)
        self.assertIn('.py', type_stats)
        
        # Verify counts
        self.assertEqual(type_stats['.txt']['count'], 3)
        self.assertEqual(type_stats['.py']['count'], 5)

    def test_largest_files(self):
        """Test finding largest files"""
        analysis = self.analyzer.analyze_directory(
            self.test_dir,
            top_files_count=5
        )
        largest_files = analysis['largest_files']
        
        # Verify correct number of files returned
        self.assertEqual(len(largest_files), 5)
        
        # Verify files are in descending size order
        for i in range(len(largest_files) - 1):
            self.assertGreaterEqual(
                largest_files[i]['size'],
                largest_files[i + 1]['size']
            )

    def test_directory_tree(self):
        """Test directory tree generation"""
        analysis = self.analyzer.analyze_directory(self.test_dir)
        tree = analysis['directory_tree']
        
        # Verify all main directories are present
        for dir_name in self.dirs:
            self.assertIn(dir_name, str(tree))
        
        # Verify tree structure
        self.assertIsInstance(tree, dict)
        self.assertIn('size', tree)
        self.assertIn('children', tree)

    def test_size_formatting(self):
        """Test human-readable size formatting"""
        test_sizes = [
            (1024, "1.0 KB"),
            (1024 * 1024, "1.0 MB"),
            (1024 * 1024 * 1024, "1.0 GB"),
            (123, "123.0 B")
        ]
        
        for size, expected in test_sizes:
            formatted = self.analyzer.format_size(size)
            self.assertEqual(formatted, expected)

    def test_export_analysis(self):
        """Test exporting analysis results"""
        analysis = self.analyzer.analyze_directory(self.test_dir)
        export_file = os.path.join(self.test_dir, "analysis.json")
        
        # Export analysis
        self.analyzer.export_analysis(analysis, export_file)
        
        # Verify export file exists and is valid JSON
        self.assertTrue(os.path.exists(export_file))
        with open(export_file, 'r') as f:
            loaded = json.load(f)
            self.assertEqual(loaded['total_size'], analysis['total_size'])

    def test_progress_tracking(self):
        """Test progress reporting during analysis"""
        progress_values = []
        
        def progress_callback(percent):
            progress_values.append(percent)
        
        # Analyze with progress tracking
        self.analyzer.analyze_directory(
            self.test_dir,
            progress_callback=progress_callback
        )
        
        # Verify progress was reported
        self.assertTrue(len(progress_values) > 0)
        self.assertEqual(progress_values[-1], 100)

    def test_error_handling(self):
        """Test error handling for various scenarios"""
        # Test non-existent directory
        with self.assertRaises(FileNotFoundError):
            self.analyzer.analyze_directory("nonexistent")
        
        # Test permission error
        if os.name == 'posix':
            restricted_dir = os.path.join(self.test_dir, "restricted")
            os.makedirs(restricted_dir)
            os.chmod(restricted_dir, 0o000)
            
            # Should skip inaccessible directories without failing
            analysis = self.analyzer.analyze_directory(self.test_dir)
            self.assertIsInstance(analysis, dict)

    def test_filters(self):
        """Test file filtering during analysis"""
        # Test extension filter
        analysis = self.analyzer.analyze_directory(
            self.test_dir,
            include_extensions=['.py', '.txt']
        )
        
        # Verify only specified extensions are included
        for file_info in analysis['files']:
            self.assertTrue(
                file_info['path'].endswith('.py') or
                file_info['path'].endswith('.txt')
            )

if __name__ == '__main__':
    unittest.main()