import os
import shutil
import tempfile
from datetime import datetime
from unittest import TestCase
from unittest.mock import MagicMock, patch
from organize import Rule, RuleDialog, MyGUI

from core.error_handler import error_handler


class TestRule(TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)
        
    def create_test_file(self, filename, content="test content"):
        filepath = os.path.join(self.test_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath
            
    def test_rule_initialization(self):
        """Test Rule object initialization with various parameters"""
        # Test minimal initialization
        rule = Rule(name="Test", destination="/tmp", file_types=[".txt"])
        self.assertEqual(rule.name, "Test")
        self.assertEqual(rule.destination, "/tmp")
        self.assertEqual(rule.file_types, [".txt"])
        self.assertIsNone(rule.contains_text)
        
        # Test full initialization
        now = datetime.now()
        rule = Rule(
            name="Full Test",
            destination="/tmp/full",
            file_types=[".txt", ".pdf"],
            created_after=now,
            created_before=now,
            modified_after=now,
            modified_before=now,
            contains_text="test"
        )
        self.assertEqual(rule.name, "Full Test")
        self.assertEqual(rule.file_types, [".txt", ".pdf"])
        self.assertEqual(rule.created_after, now)
        self.assertEqual(rule.contains_text, "test")

    def test_rule_file_type_matching(self):
        # Create test files
        txt_file = self.create_test_file("test.txt")
        pdf_file = self.create_test_file("test.pdf")
        
        # Test specific extension rule
        rule = Rule(
            name="PDF Rule",
            destination="/tmp",
            file_types=[".pdf"]
        )
        
        self.assertTrue(rule.matches(pdf_file))
        self.assertFalse(rule.matches(txt_file))
        
        # Test wildcard rule
        rule = Rule(
            name="All Files",
            destination="/tmp",
            file_types=["*"]
        )
        
        self.assertTrue(rule.matches(pdf_file))
        self.assertTrue(rule.matches(txt_file))

    def test_rule_date_matching(self):
        test_file = self.create_test_file("test.txt")
        file_time = datetime.fromtimestamp(os.path.getctime(test_file))
        
        # Test created after
        rule = Rule(
            name="Date Test",
            destination="/tmp",
            file_types=["*"],
            created_after=file_time.replace(year=file_time.year - 1)
        )
        self.assertTrue(rule.matches(test_file))
        
        # Test created before
        rule = Rule(
            name="Date Test",
            destination="/tmp",
            file_types=["*"],
            created_before=file_time.replace(year=file_time.year + 1)
        )
        self.assertTrue(rule.matches(test_file))

    def test_rule_content_matching(self):
        test_file = self.create_test_file("test.txt", "specific content here")
        
        rule = Rule(
            name="Content Test",
            destination="/tmp",
            file_types=["*"],
            contains_text="specific content"
        )
        self.assertTrue(rule.matches(test_file))
        
        rule = Rule(
            name="Content Test",
            destination="/tmp",
            file_types=["*"],
            contains_text="non-existent content"
        )
        self.assertFalse(rule.matches(test_file))

class TestMyGUI(TestCase):
    def setUp(self):
        self.app = MagicMock()
        self.gui = MyGUI()
        self.test_dir = tempfile.mkdtemp()
        self.gui.directory = self.test_dir

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_load_directory(self):
        # Create some test files
        test_files = ['test1.txt', 'test2.pdf']
        for file in test_files:
            with open(os.path.join(self.test_dir, file), 'w') as f:
                f.write('test content')

        with patch('PyQt5.QtWidgets.QFileDialog.getExistingDirectory', 
                  return_value=self.test_dir):
            self.gui.load_directory()
            self.assertEqual(self.gui.listModel.rowCount(), len(test_files))

    def test_organize_extension_based(self):
        # Create test files with different extensions
        files = {
            'doc1.txt': 'content1',
            'doc2.pdf': 'content2',
            'img1.jpg': 'content3'
        }
        
        for filename, content in files.items():
            with open(os.path.join(self.test_dir, filename), 'w') as f:
                f.write(content)

        self.gui.organize()

        # Check if directories were created
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'txt')))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'pdf')))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'jpg')))

    def test_organize_with_rules(self):
        # Create test file
        test_file = os.path.join(self.test_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('specific content')

        # Create rule
        rule_dest = os.path.join(self.test_dir, 'rule_based')
        self.gui.rules.append(Rule(
            name="Text Rule",
            destination=rule_dest,
            file_types=['.txt'],
            contains_text='specific'
        ))

        self.gui.organize()

        # Check if file was moved according to rule
        self.assertTrue(os.path.exists(os.path.join(rule_dest, 'test.txt')))

    def test_recursive_organize(self):
        # Create nested directory structure
        nested_dir = os.path.join(self.test_dir, 'nested')
        os.makedirs(nested_dir)
        
        files = {
            'test1.txt': 'content1',
            os.path.join('nested', 'test2.pdf'): 'content2'
        }
        
        for filepath, content in files.items():
            full_path = os.path.join(self.test_dir, filepath)
            with open(full_path, 'w') as f:
                f.write(content)

        self.gui.recursiveCheckBox.setChecked(True)
        self.gui.organize()

        # Check if files were organized
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'txt')))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, 'pdf')))
        
    def test_error_handling(self):
        """Test error handling in the organize method"""
        # Test with invalid directory
        self.gui.directory = "/nonexistent/path"
        with patch('logging.Logger.error') as mock_error:
            self.gui.organize()
            mock_error.assert_called()
            
        # Test with invalid rule destination
        self.gui.directory = self.test_dir
        test_file = os.path.join(self.test_dir, 'test.txt')
        with open(test_file, 'w') as f:
            f.write('test content')
            
        self.gui.rules.append(Rule(
            name="Invalid Rule",
            destination="/nonexistent/path",
            file_types=['.txt']
        ))
        
        with patch('gui.common.dialogs.show_error_dialog') as mock_error:
            self.gui.organize()
            mock_error.assert_called()
            
    def test_manage_rules(self):
        """Test rule addition and validation"""
        # Create a test rule directly
        test_rule = Rule(
            name="Test Rule",
            destination=os.path.join(self.test_dir, "test_dest"),
            file_types=[".txt"]
        )
        
        # Add the rule to GUI
        self.gui.rules.append(test_rule)
        
        # Verify rule was added
        self.assertEqual(len(self.gui.rules), 1)
        self.assertEqual(self.gui.rules[0].name, "Test Rule")
        self.assertEqual(self.gui.rules[0].file_types, [".txt"])
                
    def test_invalid_directory(self):
        """Test behavior with invalid directory path"""
        # Set an invalid directory
        self.gui.directory = "/nonexistent/path"
        
        # Try to organize
        self.gui.organize()
        
        # Nothing should happen, no errors should be raised
        self.assertEqual(self.gui.directory, "/nonexistent/path")
            
    def test_file_filtering(self):
        """Test that files are organized correctly by extension"""
        # Create test files with different extensions
        files = {
            'doc1.txt': 'content1',
            'doc2.pdf': 'content2',
            'doc3.txt': 'content3'
        }
        
        for filename, content in files.items():
            path = os.path.join(self.test_dir, filename)
            with open(path, 'w') as f:
                f.write(content)
                    
        self.gui.organize()
        
        # Check that files were organized by extension
        txt_path = os.path.join(self.test_dir, 'txt')
        pdf_path = os.path.join(self.test_dir, 'pdf')
        
        self.assertTrue(os.path.exists(txt_path))
        self.assertTrue(os.path.exists(pdf_path))
        self.assertTrue(os.path.exists(os.path.join(txt_path, 'doc1.txt')))
        self.assertTrue(os.path.exists(os.path.join(txt_path, 'doc3.txt')))
        self.assertTrue(os.path.exists(os.path.join(pdf_path, 'doc2.pdf')))
