import os
import shutil
import tempfile
from datetime import datetime
from unittest import TestCase
from unittest.mock import MagicMock, patch
from organize import Rule, RuleDialog, MyGUI

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
