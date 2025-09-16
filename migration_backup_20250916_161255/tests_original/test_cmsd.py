import os
import tempfile
import shutil
import pytest
from unittest.mock import patch
from PyQt5.QtWidgets import QApplication
from cmsd import MyGUI

@pytest.fixture
def app():
    """Fixture to create and manage the QApplication instance"""
    app = QApplication([])
    yield app
    app.quit()

@pytest.fixture
def gui(app):
    """Fixture to create the GUI instance"""
    return MyGUI()

@pytest.fixture
def test_dir():
    """Fixture to create and manage a temporary directory with test files"""
    temp_dir = tempfile.mkdtemp()
    test_files = ['test1.txt', 'test2.txt', 'test3.txt']
    for filename in test_files:
        with open(os.path.join(temp_dir, filename), 'w') as f:
            f.write('test content')
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

def test_initial_state(gui):
    """Test the initial state of the GUI"""
    assert gui.left_directory == "."
    assert gui.right_directory == "."
    assert gui.left_model.rowCount() == 0
    assert gui.right_model.rowCount() == 0
    assert len(gui.selected) == 0

@pytest.mark.parametrize("load_func,model_attr", [
    ("load_directory_left", "left_model"),
    ("load_directory_right", "right_model")])
def test_load_directory(gui, test_dir, load_func, model_attr):
    """Test loading directories into both views"""
    with patch('gui.common.dialogs.get_existing_directory', return_value=test_dir):
        getattr(gui, load_func)()
        model = getattr(gui, model_attr)
        assert model.rowCount() == 3
        filenames = [model.item(i).text() for i in range(model.rowCount())]
        assert all(name in filenames for name in ['test1.txt', 'test2.txt', 'test3.txt'])

def test_load_empty_directory(gui, test_dir):
    """Test loading an empty directory"""
    empty_dir = os.path.join(test_dir, 'empty')
    os.makedirs(empty_dir)
    with patch('gui.common.dialogs.get_existing_directory', return_value=empty_dir):
        gui.load_directory_left()
        assert gui.left_model.rowCount() == 0

def test_load_directory_with_subdirs(gui, test_dir):
    """Test that only files (not directories) are loaded"""
    subdir = os.path.join(test_dir, 'subdir')
    os.makedirs(subdir)
    with open(os.path.join(subdir, 'subfile.txt'), 'w') as f:
        f.write('test')
    with patch('gui.common.dialogs.get_existing_directory', return_value=test_dir):
        gui.load_directory_left()
        filenames = [gui.left_model.item(i).text() for i in range(gui.left_model.rowCount())]
        assert 'subdir' not in filenames
