"""Test script for the GUI migration automator."""
import unittest
from pathlib import Path
import tempfile
import shutil

from tools.gui_migration.gui_migrator_v2 import GUIMigrationAutomator


class TestGUIMigrationAutomator(unittest.TestCase):
    """A class that handles test g u i migration automator."""
    def setUp(self):
        """setup."""
        # Create a temporary workspace
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create some test files
        self.gui_file1 = self.temp_dir / "test_gui1.py"
        self.gui_file1.write_text('''
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
    def show_warning(self):
        QMessageBox.warning(self, "Warning", "This is a warning")
        
    def get_file(self):
        return QFileDialog.getOpenFileName(self, "Open File")[0]
''')

        self.gui_file2 = self.temp_dir / "test_gui2.py"
        self.gui_file2.write_text('''
from PyQt5.QtWidgets import QDialog

from core.error_handler import error_handler


class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
''')

        # Create a test file that shouldn't be detected
        self.non_gui_file = self.temp_dir / "test_non_gui.py"
        self.non_gui_file.write_text('''
def add(a, b):
    return a + b
''')

        self.automator = GUIMigrationAutomator(self.temp_dir)
        self.automator._test_mode = True  # Enable test mode

    def tearDown(self):
        """teardown."""
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir)

    def test_find_gui_files(self):
        """Test that GUI files are correctly identified."""
        gui_files = self.automator.find_gui_files()
        
        # Should find exactly 2 GUI files
        self.assertEqual(len(gui_files), 2)
        
        # Both GUI files should be in the list
        file_names = {f.name for f in gui_files}
        self.assertIn("test_gui1.py", file_names)
        self.assertIn("test_gui2.py", file_names)

    def test_analyze_gui_file(self):
        """Test that GUI file analysis creates correct migration plans."""
        plan = self.automator.analyze_gui_file(self.gui_file1)
        
        self.assertIsNotNone(plan)
        self.assertEqual(len(plan['changes']), 3)  # Inheritance, Dialog, FileDialog
        
        # Check specific changes
        changes = {c['type'] for c in plan['changes']}
        self.assertIn('inheritance', changes)
        self.assertIn('dialog', changes)
        self.assertIn('file_dialog', changes)

    def test_create_migration_scripts(self):
        """Test that migration scripts are created correctly."""
        self.automator.find_gui_files()
        self.automator.create_migration_scripts()
        
        # Check that migration scripts were created
        script1 = (
            self.automator.migration_dir / "migrate_test_gui1.py"
        )
        script2 = (
            self.automator.migration_dir / "migrate_test_gui2.py"
        )
        
        self.assertTrue(script1.exists())
        self.assertTrue(script2.exists())

    def test_apply_migrations(self):
        """Test that migrations are applied correctly."""
        self.automator.find_gui_files()
        self.automator.create_migration_scripts()
        
        # Create backups and apply migrations
        self.automator.apply_migrations(create_backups=True)
        
        # Check that backups were created
        backup1 = self.gui_file1.with_suffix('.py.bak')
        self.assertTrue(backup1.exists())
        
        # Check that files were modified
        content = self.gui_file1.read_text()
        self.assertIn('BaseWindow', content)
        self.assertIn('show_error_dialog', content)
        self.assertIn('get_open_file_name', content)


if __name__ == '__main__':
    unittest.main()
